import argparse, json
from taskworker.broker import serve
from taskworker.worker import run_workers
from taskworker.client import request, submit

def main():
    p=argparse.ArgumentParser(description="Python multiprocessing task worker")
    sub=p.add_subparsers(dest="cmd",required=True)
    b=sub.add_parser("broker"); b.add_argument("--host",default="127.0.0.1"); b.add_argument("--port",type=int,default=8000)
    w=sub.add_parser("worker"); w.add_argument("--url",default="http://127.0.0.1:8000"); w.add_argument("--count",type=int,default=4)
    s=sub.add_parser("submit"); s.add_argument("name",choices=["add","greet","uppercase"]); s.add_argument("--payload",default="{}"); s.add_argument("--url",default="http://127.0.0.1:8000")
    sub.add_parser("stats")
    a=p.parse_args()
    if a.cmd=="broker": serve(a.host,a.port)
    elif a.cmd=="worker": run_workers(a.url,a.count)
    elif a.cmd=="submit":
        data=json.loads(a.payload)
        if not isinstance(data,dict): p.error("--payload must be a JSON object")
        print(json.dumps(submit(a.url,a.name,data),indent=2))
    elif a.cmd=="stats": print(json.dumps(request("http://127.0.0.1:8000","/stats"),indent=2))
if __name__=="__main__": main()
