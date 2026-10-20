import ast,time,sys,json
sys.path.insert(0,'.')
from quandle import *; from symp import *
q=int(sys.argv[1]); a=int(sys.argv[2]) if len(sys.argv)>2 else 1
todo=json.load(open(sys.argv[3])) if len(sys.argv)>3 else None
pts,P,N=symp_quandle(q,2,a)
rows,I=load()
sel=[x for x in rows if x[I['bridge_index']]=='[3,4]']
if todo is not None: sel=[x for x in sel if x[I['name']] in set(todo)]
t=time.time(); res={}
for x in sel:
    pd=ast.literal_eval(x[I['pd_notation']]); n,cr=crossings(pd)
    c,cols=colorings(n,cr,P,N,k=4)
    cert=None
    for row in cols:
        if rank_mod([pts[j] for j in set(row.tolist())],q)==4: cert=[list(pts[j]) for j in row.tolist()]; break
    res[x[I['name']]]={'count':int(c),'cert':cert}
json.dump(res,open(f'sp4_{q}_{a}.json','w'))
print(q,a,len(sel),sum(1 for v in res.values() if v['cert']),round(time.time()-t,1))
