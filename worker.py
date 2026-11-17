import json, multiprocessing as mp, signal, time, traceback, urllib.request
from .tasks import REGISTRY

def api(base, method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(base+path, data=data, method=method,
        headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req, timeout=10) as response:
        return json.loads(response.read())

def run_loop(base, stop, poll=0.2):
    while not stop.is_set():
        try: task = api(base, "POST", "/dequeue", {}).get("task")
        except Exception:
            time.sleep(1); continue
        if task is None:
            time.sleep(poll); continue
        try:
            fn = REGISTRY.get(task["name"])
            if fn is None: raise LookupError(f"No task registered as '{task['name']}'")
            result = fn(**task["payload"])
            try: json.dumps(result); safe_result = result
            except TypeError: safe_result = str(result)
            api(base, "POST", f"/tasks/{task['id']}/ack", {"result":safe_result})
            print(f"[worker] completed {task['name']} -> {safe_result}")
        except Exception:
            error = traceback.format_exc(limit=3)
            try: api(base, "POST", f"/tasks/{task['id']}/fail", {"error":error})
            except Exception: pass
            print(f"[worker] failed {task['id']}\n{error}")

def run_workers(base="http://127.0.0.1:8000", concurrency=4):
    stop = mp.Event()
    def stop_now(*_): stop.set()
    signal.signal(signal.SIGINT, stop_now); signal.signal(signal.SIGTERM, stop_now)
    processes = [mp.Process(target=run_loop,args=(base,stop)) for _ in range(concurrency)]
    for p in processes: p.start()
    print(f"[worker] {concurrency} workers polling {base}; Ctrl+C to stop")
    for p in processes: p.join()
