import itertools, numpy as np
def symp_quandle(q,m=2,a=1):
    n=2*m
    def canon(v):
        v=tuple(x%q for x in v)
        for x in v:
            if x: inv=pow(x,-1,q); break
        # points up to sign only (t_{cv} = t_v^{c^2}); keep class v ~ -v
        w=tuple((inv*y)%q for y in v)
        # normalize so first nonzero is 1 or (choose between v and -v): pick lexicographically min of v,-v
        v1=v; v2=tuple((-y)%q for y in v)
        return min(v1,v2)
    pts=sorted({canon(v) for v in itertools.product(range(q),repeat=n) if any(v)})
    ix={p:i for i,p in enumerate(pts)}
    def form(x,y): return sum(x[i]*y[i+m]-x[i+m]*y[i] for i in range(m))%q
    M=len(pts)
    P=np.zeros((M,M),np.int32); N=np.zeros((M,M),np.int32)
    for i,u in enumerate(pts):
        for j,v in enumerate(pts):
            f=form(v,u)
            P[i,j]=ix[canon([v[k]+a*f*u[k] for k in range(n)])]
            N[i,j]=ix[canon([v[k]-a*f*u[k] for k in range(n)])]
    return pts,P,N
def rank_mod(vecs,q):
    A=[list(v) for v in vecs]; r=0; cols=len(A[0]) if A else 0
    for c in range(cols):
        piv=None
        for i in range(r,len(A)):
            if A[i][c]%q: piv=i;break
        if piv is None: continue
        A[r],A[piv]=A[piv],A[r]; inv=pow(A[r][c],-1,q)
        A[r]=[(x*inv)%q for x in A[r]]
        for i in range(len(A)):
            if i!=r and A[i][c]%q:
                f=A[i][c]; A[i]=[(x-f*y)%q for x,y in zip(A[i],A[r])]
        r+=1
    return r
