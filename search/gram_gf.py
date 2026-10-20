import ast,time,sys,json,itertools,numpy as np
sys.path.insert(0,'.')
from quandle import crossings, plan; from wirt import load; from gf import make
PAIRS=[(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]
def search(n,cr,q,chunk=400_000):
    A,M,N,Z,O,els=make(q)
    s,steps=plan(n,cr,4)
    sub=lambda x,y: A[x,N[y]]
    def form(x,y,W):
        acc=np.full(x.shape[0],Z,np.int32)
        for k,(i,j) in enumerate(PAIRS):
            acc=A[acc,M[W[:,k],sub(M[x[:,i],y[:,j]],M[x[:,j],y[:,i]])]]
        return acc
    total=q**6
    for start in range(0,total,chunk):
        idx=np.arange(start,min(total,start+chunk),dtype=np.int64)
        W=np.stack([(idx//q**k)%q for k in range(6)],1).astype(np.int32)
        pf=sub(A[M[W[:,0],W[:,5]],M[W[:,2],W[:,3]]],M[W[:,1],W[:,4]])
        W=W[pf!=Z]; K=len(W)
        if K==0: continue
        col=[None]*n
        for i,si in enumerate(s):
            v=np.full((K,4),Z,np.int32); v[:,i]=O; col[si]=v
        def tv(src,o,e):
            c=form(col[src],col[o],W)
            if e==-1: c=N[c]
            return A[col[src],M[c[:,None],col[o]]]
        for t,o,src,e in steps: col[t]=tv(src,o,e)
        ok=np.ones(K,bool)
        for o,u,v,e in cr:
            w=tv(u,o,e)
            # equal as transvections: w = c*v with c^2=1 in char!=2 ; in general t_w=t_v iff w=±v (char 2: w=v)
            ok&=((w==col[v]).all(1))|((w==N[col[v]]).all(1))
            if not ok.any(): break
        hit=np.nonzero(ok)[0]
        if len(hit):
            k=hit[0]; return {'q':q,'W':[els[x] for x in W[k].tolist()],'colors':[[els[x] for x in col[a][k].tolist()] for a in range(n)]}
    return None
if __name__=='__main__':
    q=int(sys.argv[1]); todo=json.load(open(sys.argv[2])); out=sys.argv[3]
    rows,I=load(); S=set(todo); sel=[x for x in rows if x[I['name']] in S]
    res={}; t=time.time()
    for x in sel:
        pd=ast.literal_eval(x[I['pd_notation']]); n,cr=crossings(pd)
        f=search(n,cr,q)
        if f: res[x[I['name']]]=f
        json.dump(res,open(out,'w'))
    print('sp-gram-gf',q,len(sel),len(res),round(time.time()-t,1),flush=True)
