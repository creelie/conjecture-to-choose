import itertools, numpy as np, ast
from wirt import load, arcs, closure
def crossings(pd):
    n2=2*len(pd)
    par={}
    def f(x):
        while par.setdefault(x,x)!=x: x=par[x]
        return x
    for a,b,c,d in pd:
        f(a);f(c);par[f(b)]=f(d)
    roots=sorted({f(e) for cr in pd for e in cr}); idx={r:i for i,r in enumerate(roots)}
    out=[]
    for a,b,c,d in pd:
        eps = 1 if b==d%n2+1 else -1
        out.append((idx[f(b)],idx[f(a)],idx[f(c)],eps))
    return len(roots),out
def plan(n,cr,k):
    # seeds + ordered propagation steps (target, o, src, mode) mode: 'f' target=conj^eps(o,src); 'b' target=conj^-eps(o,src)
    for s in itertools.combinations(range(n),k):
        known=set(s); steps=[]; ch=True
        while ch:
            ch=False
            for o,u,v,e in cr:
                if o in known:
                    if u in known and v not in known: steps.append((v,o,u,e)); known.add(v); ch=True
                    elif v in known and u not in known: steps.append((u,o,v,-e)); known.add(u); ch=True
        if len(known)==n: return s,steps
    return None
def colorings(n,cr,P,N,k=4,fix0=True,maxkeep=5):
    """P[o,a]=conj(o,a), N[o,a]=conj^-1(o,a). returns (count, examples) with seed0 fixed to 0 if fix0"""
    pl=plan(n,cr,k)
    s,steps=pl
    m=P.shape[0]
    grids=np.meshgrid(*([np.array([0])] if fix0 else [np.arange(m)]),*[np.arange(m)]*(k-1),indexing='ij')
    col=[None]*n
    for i,si in enumerate(s): col[si]=grids[i].ravel()
    for t,o,src,e in steps:
        col[t]=(P if e==1 else N)[col[o],col[src]]
    ok=np.ones(col[0].shape,bool)
    for o,u,v,e in cr:
        ok&=( (P if e==1 else N)[col[o],col[u]]==col[v])
    idx=np.nonzero(ok)[0]
    return len(idx), np.stack([c[idx] for c in col],1)
