import ast,time,sys,json,numpy as np
sys.path.insert(0,'.')
from quandle import crossings, plan; from wirt import load; from symp import symp_quandle, rank_mod
q=int(sys.argv[1]); a=int(sys.argv[2]); out=sys.argv[3]; todo=json.load(open(sys.argv[4])) if len(sys.argv)>4 else None
pts,P,N=symp_quandle(q,2,a); M=len(pts); ix={p:i for i,p in enumerate(pts)}
def can(v):
    v=tuple(x%q for x in v); w=tuple((-x)%q for x in v); return min(v,w)
v0=ix[can((1,0,0,0))]
reps=[v0, ix[can((0,1,0,0))]]+[ix[can((0,0,c,0))] for c in range(1,(q-1)//2+1)]
rows,I=load()
sel=[x for x in rows if x[I['bridge_index']]=='[3,4]']
if todo is not None: S=set(todo); sel=[x for x in sel if x[I['name']] in S]
t=time.time(); res={}
for x in sel:
    pd=ast.literal_eval(x[I['pd_notation']]); n,cr=crossings(pd)
    s,steps=plan(n,cr,4)
    g3,g4=np.meshgrid(np.arange(M),np.arange(M),indexing='ij'); g3=g3.ravel(); g4=g4.ravel()
    cert=None; total=0
    for r in reps:
        col=[None]*n
        col[s[0]]=np.full(g3.shape,v0); col[s[1]]=np.full(g3.shape,r); col[s[2]]=g3; col[s[3]]=g4
        for tt,o,src,e in steps: col[tt]=(P if e==1 else N)[col[o],col[src]]
        ok=np.ones(g3.shape,bool)
        for o,u,v,e in cr: ok&=((P if e==1 else N)[col[o],col[u]]==col[v])
        idx=np.nonzero(ok)[0]; total+=len(idx)
        for k in idx:
            row=[int(c[k]) for c in col]
            if rank_mod([pts[j] for j in set(row)],q)==4: cert=[list(pts[j]) for j in row]; break
        if cert: break
    res[x[I['name']]]={'sols':total,'cert':cert}
json.dump(res,open(out,'w'))
print(q,a,len(sel),sum(1 for v in res.values() if v['cert']),round(time.time()-t,1),flush=True)
