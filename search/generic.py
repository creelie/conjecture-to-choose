import ast,time,sys,json,itertools,numpy as np
sys.path.insert(0,'.')
from quandle import crossings, plan; from wirt import load; from symp import rank_mod
def orth_quandle(q,diag,sq):
    """reflections r_v, v anisotropic with Q(v) in square class sq (0: squares,1: nonsquares); points projective"""
    squares={(x*x)%q for x in range(1,q)}
    def Q(v): return sum(d*x*x for d,x in zip(diag,v))%q
    def B(u,v): return sum(d*x*y for d,x,y in zip(diag,u,v))%q
    def canon(v):
        v=[x%q for x in v]
        for x in v:
            if x: inv=pow(x,-1,q); break
        return tuple((inv*y)%q for y in v)
    pts=sorted({canon(v) for v in itertools.product(range(q),repeat=len(diag)) if any(v) and Q(v)!=0 and ((Q(v) in squares)==(sq==0))})
    ix={p:i for i,p in enumerate(pts)}; M=len(pts)
    P=np.zeros((M,M),np.int32)
    for i,u in enumerate(pts):
        qu=pow(Q(u),-1,q)
        for j,v in enumerate(pts):
            c=(2*B(v,u)*qu)%q
            P[i,j]=ix[canon([v[k]-c*u[k] for k in range(len(diag))])]
    return pts,P,P
def run(pts,P,N,q,names,label,seed0s=(0,),maxM2=2_000_000):
    rows,I=load(); S=set(names)
    sel=[x for x in rows if x[I['name']] in S]
    M=len(pts); res={}
    t=time.time()
    for x in sel:
        pd=ast.literal_eval(x[I['pd_notation']]); n,cr=crossings(pd)
        s,steps=plan(n,cr,4)
        cert=None
        g3,g4=np.meshgrid(np.arange(M),np.arange(M),indexing='ij'); g3=g3.ravel(); g4=g4.ravel()
        for r0 in seed0s:
            for r1 in range(M):
                col=[None]*n
                col[s[0]]=np.full(g3.shape,r0); col[s[1]]=np.full(g3.shape,r1); col[s[2]]=g3; col[s[3]]=g4
                for tt,o,src,e in steps: col[tt]=(P if e==1 else N)[col[o],col[src]]
                ok=np.ones(g3.shape,bool)
                for o,u,v,e in cr:
                    ok&=((P if e==1 else N)[col[o],col[u]]==col[v])
                    if not ok.any(): break
                for k in np.nonzero(ok)[0]:
                    row=[int(c[k]) for c in col]
                    if rank_mod([pts[j] for j in set(row)],q)==4: cert=[list(pts[j]) for j in row]; break
                if cert: break
            if cert: break
        res[x[I['name']]]={'cert':cert,'quandle':label}
    print(label,len(sel),sum(1 for v in res.values() if v['cert']),round(time.time()-t,1),flush=True)
    return res
