from __future__ import annotations
import socket, threading, time
from dataclasses import dataclass
from typing import Callable
from urllib.parse import unquote

@dataclass(frozen=True)
class Subscription:
    alias: str
    name: str
    type: str = "float"
    index: int = -1

class XPlaneBridge:
    def __init__(self, host="127.0.0.1", port=49050, listen_port=49051):
        self.target=(host,port); self.listen_port=listen_port
        self.sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.sock.bind((host,listen_port)); self.sock.settimeout(0.25)
        self.telemetry: dict[str, object]={}
        self.last_rx=0.0; self.running=False; self.thread=None
        self.listeners: list[Callable[[dict[str,object]],None]]=[]

    def start(self):
        if self.running: return
        self.running=True; self.thread=threading.Thread(target=self._loop,daemon=True); self.thread.start()
        self.send("PING")

    def close(self):
        self.running=False
        if self.thread: self.thread.join(timeout=1)
        self.sock.close()

    @property
    def connected(self): return time.monotonic()-self.last_rx < 1.0
    def send(self,msg:str): self.sock.sendto(msg.encode("utf-8"),self.target)
    def clear_subscriptions(self): self.send("UNSUBALL")
    def subscribe(self,s:Subscription): self.send(f"SUB|{s.alias}|{s.type}|{s.index}|{s.name}")
    def command(self,name:str,phase="once"): self.send(f"CMD|{name}|{phase}")
    def set_dataref(self,name:str,value:float|int,typ="float"): self.send(f"SET|{name}|{typ}|{value}")

    def _loop(self):
        while self.running:
            try: raw,_=self.sock.recvfrom(8192)
            except socket.timeout: continue
            except OSError: break
            self.last_rx=time.monotonic()
            msg=raw.decode("utf-8","replace")
            if not msg.startswith("TLM|"): continue
            parts=msg.split("|")[2:]; update={}
            for item in parts:
                if "=" not in item: continue
                k,v=item.split("=",1)
                if v=="~": update[k]=None; continue
                v=unquote(v)
                try:
                    update[k]=float(v)
                except ValueError: update[k]=v.rstrip("\x00")
            self.telemetry.update(update)
            for fn in list(self.listeners):
                try: fn(dict(self.telemetry))
                except Exception: pass
