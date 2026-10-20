"""Knot group -> O(B) over F_q (q odd prime), meridians -> reflections; seeds e_1..e_4 with B(e_i,e_i)=s."""
import ast,time,sys,json,itertools,numpy as np
sys.path.insert(0,'.')
from quandle import crossings, plan; from wirt import load
PAIRS=[(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]
def det4(B,q):
    s=np.zeros(B.shape[0],np.int64)
    for p in itertools.permutations(range(4)):
        inv=sum(1 for i in range(4) for j in range(i+1,4) if p[i]>p[j]); t=np.ones(B.shape[0],np.int64)
        for i in range(4): t=(t*B[:,i,p[i]])%q
        s=(s+(-1)**inv*t)%q
    return s
def search(n,cr,q,s_cls,chunk=500_000):
    s,steps=plan(n,cr,4); INV=np.array([0]+[pow(x,-1,q) for x in range(1,q)],np.int64)
    total=q**6
    for start in range(0,total,chunk):
        idx=np.arange(start,min(total,start+chunk),dtype=np.int64); K=len(idx)
        B=np.zeros((K,4,4),np.int64)
        for i in range(4): B[:,i,i]=s_cls
        for k,(i,j) in enumerate(PAIRS): B[:,i,j]=B[:,j,i]=(idx//q**k)%q
        keep=det4(B,q)!=0; B=B[keep]; K=len(B)
        if K==0: continue
        Bf=lambda x,y: np.einsum('ki,kij,kj->k',x,B,y)%q
        col=[None]*n
        for i,si in enumerate(s):
            v=np.zeros((K,4),np.int64); v[:,i]=1; col[si]=v
        def refl(src,o):
            c=(2*Bf(col[src],col[o])*INV[Bf(col[o],col[o])])%q
            return (col[src]-c[:,None]*col[o])%q
        for t,o,src,e in steps: col[t]=refl(src,o)
        ok=np.ones(K,bool)
        for o,u,v,e in cr:
            w=refl(u,o)
            ok&=(((w-col[v])%q==0).all(1))|(((w+col[v])%q==0).all(1))
            if not ok.any(): break
        hit=np.nonzero(ok)[0]
        if len(hit):
            k=hit[0]; return {'q':q,'B':B[k].tolist(),'colors':[col[a][k].tolist() for a in range(n)]}
    return None
if __name__=='__main__':
    q=int(sys.argv[1]); todo=json.load(open(sys.argv[2])); out=sys.argv[3]
    nonsq=next(x for x in range(2,q) if pow(x,(q-1)//2,q)==q-1)
    rows,I=load(); S=set(todo); sel=[x for x in rows if x[I['name']] in S]
    res={}; t=time.time()
    for x in sel:
        pd=ast.literal_eval(x[I['pd_notation']]); n,cr=crossings(pd)
        for sc in (1,nonsq):
            f=search(n,cr,q,sc)
            if f: res[x[I['name']]]=f; break
        json.dump(res,open(out,'w'))
    print('o-gram',q,len(sel),len(res),round(time.time()-t,1),flush=True)
