import sys,json,ast; sys.path.insert(0,'.')
from wirt import load
def uf_labels(pd):
    par={}
    def f(x):
        while par.setdefault(x,x)!=x: x=par[x]
        return x
    for a,b,c,d in pd: f(a);f(c);par[f(b)]=f(d)
    roots=sorted({f(e) for cr in pd for e in cr}); idx={r:i for i,r in enumerate(roots)}
    return {e:idx[f(e)] for cr in pd for e in cr}
def form_std(x,y,q): return (x[0]*y[2]+x[1]*y[3]-x[2]*y[0]-x[3]*y[1])%q
def T_sp(u,q,form):
    # x -> x + <x,u> u ; column j = image of e_j
    M=[[0]*4 for _ in range(4)]
    for j in range(4):
        e=[int(k==j) for k in range(4)]; c=form(e,u)
        for i in range(4): M[i][j]=(e[i]+c*u[i])%q
    return M
def R_o(u,q,diag):
    B=lambda x,y: sum(d*a*b for d,a,b in zip(diag,x,y))%q
    iq=pow(B(u,u),-1,q); M=[[0]*4 for _ in range(4)]
    for j in range(4):
        e=[int(k==j) for k in range(4)]; c=2*B(e,u)*iq%q
        for i in range(4): M[i][j]=(e[i]-c*u[i])%q
    return M
def mats_for(pd,cert,kind,q,extra=None):
    lab=uf_labels(pd)
    if kind=='sp': per=[T_sp(v,q,lambda x,y:form_std(x,y,q)) for v in cert]
    elif kind=='o': per=[R_o(v,q,extra) for v in cert]
    elif kind=='sp-gram':
        W=extra; P=[(0,1),(0,2),(0,3),(1,2),(1,3),(2,3)]
        fm=lambda x,y: sum(w*(x[i]*y[j]-x[j]*y[i]) for w,(i,j) in zip(W,P))%q
        per=[T_sp(v,q,fm) for v in cert]
    elif kind=='o-gram': per=[R_gram(v,q,extra) for v in cert]
    elif kind=='gl':
        V,F=extra
        per=[[[ (int(i==j)+V[a][i]*F[a][j])%q for j in range(4)] for i in range(4)] for a in range(len(V))]
    return {e:per[l] for e,l in lab.items()}
def R_gram(u,q,B):
    Bf=lambda x,y: sum(x[i]*B[i][j]*y[j] for i in range(4) for j in range(4))%q
    iq=pow(Bf(u,u),-1,q); M=[[0]*4 for _ in range(4)]
    for j in range(4):
        e=[int(k==j) for k in range(4)]; c=2*Bf(e,u)*iq%q
        for i in range(4): M[i][j]=(e[i]-c*u[i])%q
    return M
