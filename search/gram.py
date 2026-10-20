"""Search for representations of a knot group into Sp(4,q) (meridians -> transvections) whose
seed colors form a basis, parametrised by the Gram matrix of the four seed vectors."""
import ast,time,sys,json,itertools,numpy as np
sys.path.insert(0,'.')
from quandle import crossings, plan; from wirt import load
PAIRS=[(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]
def form(x,y,W,q):
    s=0
    for k,(i,j) in enumerate(PAIRS):
        s=s+W[:,k]*((x[:,i]*y[:,j]-x[:,j]*y[:,i])%q)
    return s%q
def search_sp(n,cr,q,chunk=1_000_000,want=1):
    s,steps=plan(n,cr,4)
    allW=itertools.product(range(q),repeat=6)
    found=[]
    total=q**6
    for start in range(0,total,chunk):
        # build chunk of W
        idx=np.arange(start,min(total,start+chunk),dtype=np.int64)
        W=np.stack([(idx//q**k)%q for k in range(6)],1)
        pf=(W[:,0]*W[:,5]-W[:,1]*W[:,4]+W[:,2]*W[:,3])%q
        keep=pf!=0; W=W[keep]; K=len(W)
        if K==0: continue
        col=[None]*n
        for i,si in enumerate(s):
            v=np.zeros((K,4),np.int64); v[:,i]=1; col[si]=v
        for t,o,src,e in steps:
            c=form(col[src],col[o],W,q)
            col[t]=(col[src]+e*c[:,None]*col[o])%q
        ok=np.ones(K,bool)
        for o,u,v,e in cr:
            c=form(col[u],col[o],W,q)
            w=(col[u]+e*c[:,None]*col[o])%q
            ok&=(((w-col[v])%q==0).all(1))|(((w+col[v])%q==0).all(1))
            if not ok.any(): break
        for k in np.nonzero(ok)[0][:want]:
            found.append({'W':W[k].tolist(),'colors':[col[a][k].tolist() for a in range(n)]})
        if len(found)>=want: break
    return found
if __name__=='__main__':
    q=int(sys.argv[1]); todo=json.load(open(sys.argv[2])); out=sys.argv[3]
    rows,I=load(); S=set(todo); sel=[x for x in rows if x[I['name']] in S]
    res={}; t=time.time()
    for x in sel:
        pd=ast.literal_eval(x[I['pd_notation']]); n,cr=crossings(pd)
        f=search_sp(n,cr,q)
        if f: res[x[I['name']]]={'q':q,'kind':'sp-gram',**f[0]}
        json.dump(res,open(out,'w'))
    print('sp-gram',q,len(sel),len(res),round(time.time()-t,1),flush=True)
