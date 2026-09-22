#include "XPLMDataAccess.h"
#include "XPLMPlugin.h"
#include "XPLMProcessing.h"
#include "XPLMUtilities.h"

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <sstream>
#include <string>
#include <unordered_map>
#include <vector>

#if defined(_WIN32)
  #include <winsock2.h>
  #include <ws2tcpip.h>
  using socket_t = SOCKET;
  constexpr socket_t INVALID_SOCK = INVALID_SOCKET;
#else
  #include <arpa/inet.h>
  #include <fcntl.h>
  #include <netinet/in.h>
  #include <sys/socket.h>
  #include <unistd.h>
  using socket_t = int;
  constexpr socket_t INVALID_SOCK = -1;
#endif

namespace {
constexpr int kPort = 49050;
constexpr float kLoopSec = 0.10f;
constexpr size_t kMaxPacket = 8192;

struct Subscription {
    std::string alias;
    std::string name;
    std::string type;
    int index = -1;
    XPLMDataRef ref = nullptr;
    std::chrono::steady_clock::time_point lastResolve{};
};

socket_t gSock = INVALID_SOCK;
sockaddr_in gClient{};
bool gHasClient = false;
std::vector<Subscription> gSubs;

void log(const std::string& s) {
    XPLMDebugString(("[AICopilotBridge] " + s + "\n").c_str());
}

void closeSocket() {
    if (gSock == INVALID_SOCK) return;
#if defined(_WIN32)
    closesocket(gSock);
    WSACleanup();
#else
    close(gSock);
#endif
    gSock = INVALID_SOCK;
}

bool initSocket() {
#if defined(_WIN32)
    WSADATA wsa{};
    if (WSAStartup(MAKEWORD(2,2), &wsa) != 0) return false;
#endif
    gSock = ::socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (gSock == INVALID_SOCK) return false;

    int reuse = 1;
    setsockopt(gSock, SOL_SOCKET, SO_REUSEADDR, reinterpret_cast<const char*>(&reuse), sizeof(reuse));
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = htons(kPort);
    if (::bind(gSock, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) != 0) {
        closeSocket();
        return false;
    }
#if defined(_WIN32)
    u_long mode = 1;
    ioctlsocket(gSock, FIONBIO, &mode);
#else
    int flags = fcntl(gSock, F_GETFL, 0);
    fcntl(gSock, F_SETFL, flags | O_NONBLOCK);
#endif
    return true;
}

std::vector<std::string> split(const std::string& s, char delim) {
    std::vector<std::string> out;
    std::string item;
    std::stringstream ss(s);
    while (std::getline(ss, item, delim)) out.push_back(item);
    return out;
}

std::string pctEncode(const std::string& in) {
    static const char* hex = "0123456789ABCDEF";
    std::string out;
    for (unsigned char c : in) {
        if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') ||
            (c >= '0' && c <= '9') || c=='_' || c=='-' || c=='.' || c=='/' || c==' ') {
            out.push_back(static_cast<char>(c));
        } else {
            out.push_back('%'); out.push_back(hex[c >> 4]); out.push_back(hex[c & 0x0F]);
        }
    }
    return out;
}

void sendToClient(const std::string& msg) {
    if (!gHasClient || gSock == INVALID_SOCK) return;
    sendto(gSock, msg.c_str(), static_cast<int>(msg.size()), 0,
           reinterpret_cast<sockaddr*>(&gClient), sizeof(gClient));
}

XPLMDataRef resolve(const std::string& name) { return XPLMFindDataRef(name.c_str()); }

std::string readSub(Subscription& s) {
    auto now = std::chrono::steady_clock::now();
    if (!s.ref && (s.lastResolve.time_since_epoch().count() == 0 || now - s.lastResolve > std::chrono::seconds(5))) {
        s.ref = resolve(s.name);
        s.lastResolve = now;
    }
    if (!s.ref) return "~";
    char buf[512]{};
    if (s.type == "int") return std::to_string(XPLMGetDatai(s.ref));
    if (s.type == "double") return std::to_string(XPLMGetDatad(s.ref));
    if (s.type == "string") {
        int n = XPLMGetDatab(s.ref, buf, 0, static_cast<int>(sizeof(buf)-1));
        if (n <= 0) return "";
        n = std::min(n, static_cast<int>(sizeof(buf)-1));
        buf[n] = '\0';
        return pctEncode(std::string(buf));
    }
    if (s.type == "float_array") {
        float v = 0.0f;
        int idx = std::max(0, s.index);
        int got = XPLMGetDatavf(s.ref, &v, idx, 1);
        return got == 1 ? std::to_string(v) : "~";
    }
    if (s.type == "int_array") {
        int v = 0;
        int idx = std::max(0, s.index);
        int got = XPLMGetDatavi(s.ref, &v, idx, 1);
        return got == 1 ? std::to_string(v) : "~";
    }
    return std::to_string(XPLMGetDataf(s.ref));
}

void handlePacket(const std::string& msg) {
    auto p = split(msg, '|');
    if (p.empty()) return;
    if (p[0] == "PING") { sendToClient("PONG|1"); return; }
    if (p[0] == "UNSUBALL") { gSubs.clear(); sendToClient("ACK|UNSUBALL"); return; }
    if (p[0] == "SUB" && p.size() >= 5) {
        Subscription s;
        s.alias = p[1]; s.type = p[2]; s.index = std::stoi(p[3]); s.name = p[4];
        s.ref = resolve(s.name); s.lastResolve = std::chrono::steady_clock::now();
        auto it = std::find_if(gSubs.begin(), gSubs.end(), [&](const auto& x){ return x.alias == s.alias; });
        if (it == gSubs.end()) gSubs.push_back(std::move(s)); else *it = std::move(s);
        sendToClient("ACK|SUB|" + p[1]);
        return;
    }
    if (p[0] == "CMD" && p.size() >= 3) {
        XPLMCommandRef c = XPLMFindCommand(p[1].c_str());
        if (!c) { sendToClient("ERR|CMD_NOT_FOUND|" + p[1]); return; }
        if (p[2] == "begin") XPLMCommandBegin(c);
        else if (p[2] == "end") XPLMCommandEnd(c);
        else XPLMCommandOnce(c);
        sendToClient("ACK|CMD|" + p[1]);
        return;
    }
    if (p[0] == "SET" && p.size() >= 4) {
        XPLMDataRef r = XPLMFindDataRef(p[1].c_str());
        if (!r) { sendToClient("ERR|DREF_NOT_FOUND|" + p[1]); return; }
        if (!XPLMCanWriteDataRef(r)) { sendToClient("ERR|DREF_READONLY|" + p[1]); return; }
        try {
            if (p[2] == "int") XPLMSetDatai(r, std::stoi(p[3]));
            else if (p[2] == "double") XPLMSetDatad(r, std::stod(p[3]));
            else XPLMSetDataf(r, std::stof(p[3]));
            sendToClient("ACK|SET|" + p[1]);
        } catch (...) { sendToClient("ERR|BAD_VALUE|" + p[1]); }
        return;
    }
}

void pollNetwork() {
    if (gSock == INVALID_SOCK) return;
    for (int i=0; i<32; ++i) {
        char buf[kMaxPacket]{};
        sockaddr_in from{};
#if defined(_WIN32)
        int len = sizeof(from);
#else
        socklen_t len = sizeof(from);
#endif
        int n = recvfrom(gSock, buf, static_cast<int>(sizeof(buf)-1), 0,
                         reinterpret_cast<sockaddr*>(&from), &len);
        if (n <= 0) break;
        // Accept localhost only.
        if (ntohl(from.sin_addr.s_addr) != INADDR_LOOPBACK) continue;
        gClient = from; gHasClient = true;
        handlePacket(std::string(buf, n));
    }
}

void sendTelemetry() {
    if (!gHasClient || gSubs.empty()) return;
    auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::system_clock::now().time_since_epoch()).count();
    std::ostringstream os; os << "TLM|" << ms;
    for (auto& s : gSubs) os << '|' << s.alias << '=' << readSub(s);
    auto msg = os.str();
    if (msg.size() < kMaxPacket) sendToClient(msg);
}

float flightLoop(float, float, int, void*) {
    pollNetwork();
    sendTelemetry();
    return kLoopSec;
}
} // namespace

PLUGIN_API int XPluginStart(char* outName, char* outSig, char* outDesc) {
    std::strcpy(outName, "AI Copilot Bridge");
    std::strcpy(outSig, "org.openai.xplane.aicopilot.bridge");
    std::strcpy(outDesc, "Local bridge for AI copilot telemetry and cockpit actions.");
    if (!initSocket()) { log("Failed to bind UDP 127.0.0.1:49050"); return 0; }
    XPLMRegisterFlightLoopCallback(flightLoop, kLoopSec, nullptr);
    log("Started on UDP 127.0.0.1:49050");
    return 1;
}

PLUGIN_API void XPluginStop(void) {
    XPLMUnregisterFlightLoopCallback(flightLoop, nullptr);
    closeSocket();
    gSubs.clear();
    log("Stopped");
}
PLUGIN_API int XPluginEnable(void) { return 1; }
PLUGIN_API void XPluginDisable(void) {}
PLUGIN_API void XPluginReceiveMessage(XPLMPluginID, int, void*) {}
