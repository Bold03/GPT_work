from __future__ import annotations
import json, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

class StatusServer:
    def __init__(self,app,host="127.0.0.1",port=8765): self.app=app; self.addr=(host,port); self.server=None; self.thread=None
    def start(self):
        app=self.app
        class H(BaseHTTPRequestHandler):
            def _send(self,code,obj):
                b=json.dumps(obj).encode(); self.send_response(code); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(b))); self.end_headers(); self.wfile.write(b)
            def do_GET(self):
                if self.path=="/status": self._send(200,app.status())
                else: self._send(404,{"error":"not_found"})
            def do_POST(self):
                if self.path!="/command": return self._send(404,{"error":"not_found"})
                try:
                    n=int(self.headers.get("Content-Length","0")); obj=json.loads(self.rfile.read(n) or b"{}")
                    self._send(200,app.handle_text(str(obj.get("text","")),obj.get("language")))
                except Exception as e: self._send(400,{"error":str(e)})
            def log_message(self,*args): pass
        self.server=ThreadingHTTPServer(self.addr,H); self.thread=threading.Thread(target=self.server.serve_forever,daemon=True); self.thread.start()
    def stop(self):
        if self.server: self.server.shutdown(); self.server.server_close()
