import json, threading, time, uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

class State:
    def __init__(self):
        self.lock = threading.Lock()
        self.pending, self.leased, self.completed, self.failed = [], {}, {}, {}
        self.lease_seconds = 30

    def recover(self):
        now = time.time()
        for task_id in [k for k,v in self.leased.items() if v["lease_until"] <= now]:
            item = self.leased.pop(task_id)
            item.pop("lease_until", None)
            self.pending.append(item)

    def submit(self, name, payload):
        item = {"id": uuid.uuid4().hex, "name": name, "payload": payload, "attempts": 0}
        with self.lock: self.pending.append(item)
        return item

    def dequeue(self):
        with self.lock:
            self.recover()
            if not self.pending: return None
            item = self.pending.pop(0)
            item["attempts"] += 1
            item["lease_until"] = time.time() + self.lease_seconds
            self.leased[item["id"]] = item
            return {k:v for k,v in item.items() if k != "lease_until"}

    def finish(self, task_id, result, failed=False):
        with self.lock:
            item = self.leased.pop(task_id, None)
            if item is None: return False
            (self.failed if failed else self.completed)[task_id] = {
                "task": item, "result" if not failed else "error": result}
            return True

STATE = State()

class Handler(BaseHTTPRequestHandler):
    def send_json(self, code, data):
        raw = json.dumps(data).encode()
        self.send_response(code); self.send_header("Content-Type","application/json")
        self.send_header("Content-Length",str(len(raw))); self.end_headers(); self.wfile.write(raw)
    def body(self):
        n = int(self.headers.get("Content-Length", "0"))
        return json.loads(self.rfile.read(n) or b"{}")
    def do_GET(self):
        if self.path == "/health": return self.send_json(200, {"ok": True})
        if self.path == "/stats":
            with STATE.lock:
                return self.send_json(200, {k:len(getattr(STATE,k)) for k in ("pending","leased","completed","failed")})
        self.send_json(404, {"error":"Not found"})
    def do_POST(self):
        try:
            data = self.body()
            if self.path == "/submit":
                if not isinstance(data.get("name"), str) or not isinstance(data.get("payload",{}), dict):
                    return self.send_json(400, {"error":"Expected task name and object payload"})
                return self.send_json(201, {"task":STATE.submit(data["name"],data.get("payload",{}))})
            if self.path == "/dequeue":
                return self.send_json(200, {"task":STATE.dequeue()})
            parts = self.path.strip("/").split("/")
            if len(parts)==3 and parts[0]=="tasks" and parts[2] in ("ack","fail"):
                ok = STATE.finish(parts[1], data.get("result") if parts[2]=="ack" else data.get("error","Unknown error"), parts[2]=="fail")
                return self.send_json(200 if ok else 404, {"ok":ok})
            self.send_json(404, {"error":"Not found"})
        except Exception as exc:
            self.send_json(400, {"error":str(exc)})
    def log_message(self, fmt, *args): print("[broker] " + fmt % args)

def serve(host="127.0.0.1", port=8000):
    server = ThreadingHTTPServer((host,port), Handler)
    print(f"[broker] listening at http://{host}:{port}")
    try: server.serve_forever()
    except KeyboardInterrupt: print("\n[broker] stopping")
    finally: server.server_close()
