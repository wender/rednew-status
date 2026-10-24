import json,time,socket,urllib.request,ssl,os
S=json.load(open('services.json'));now=int(time.time())
class NR(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*a,**k): return None
op=urllib.request.build_opener(NR)
def http(s):
    t=time.time()
    try:
        r=op.open(urllib.request.Request(s['url'],headers={'User-Agent':'rednew-status'}),timeout=15);c=r.status
    except urllib.error.HTTPError as e: c=e.code
    except Exception: c=0
    return c,int((time.time()-t)*1000)
def tcp(s):
    h,p=s['tcp'].split(':');t=time.time()
    try: socket.create_connection((h,int(p)),10).close();c=1
    except Exception: c=0
    return c,int((time.time()-t)*1000)
hist=json.load(open('data/history.json')) if os.path.exists('data/history.json') else {}
inc=json.load(open('data/incidents.json')) if os.path.exists('data/incidents.json') else []
out=[]
for s in S:
    c,ms=tcp(s) if 'tcp' in s else http(s)
    up = c==1 if 'tcp' in s else c in s['ok']
    h=hist.setdefault(s['id'],[]);prev=h[-1][1] if h else 1
    h.append([now,1 if up else 0,ms]);hist[s['id']]=h[-8640:]
    if prev and not up: inc.insert(0,{"id":s['id'],"name":s['name'],"start":now,"end":None,"code":c})
    if up and not prev:
        for i in inc:
            if i['id']==s['id'] and i['end'] is None: i['end']=now
    def upt(sec):
        x=[p[1] for p in hist[s['id']] if p[0]>=now-sec];return round(100*sum(x)/len(x),2) if x else None
    out.append({**{k:s[k] for k in ('id','group','name')},"url":s.get('url'),"up":up,"code":c,"ms":ms,"uptime24h":upt(86400),"uptime7d":upt(604800),"uptime30d":upt(2592000)})
json.dump(hist,open('data/history.json','w'),separators=(',',':'))
json.dump(inc[:100],open('data/incidents.json','w'),indent=1)
json.dump({"updated":now,"services":out},open('data/status.json','w'),indent=1)
