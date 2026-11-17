import json, urllib.request
def request(base,path,body=None):
    data=json.dumps(body).encode() if body is not None else None
    req=urllib.request.Request(base+path,data=data,method="POST" if body is not None else "GET",
        headers={"Content-Type":"application/json"})
    with urllib.request.urlopen(req,timeout=10) as r: return json.loads(r.read())
def submit(base,name,payload): return request(base,"/submit",{"name":name,"payload":payload})
