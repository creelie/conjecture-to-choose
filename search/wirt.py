import csv, itertools, random, sys, ast, warnings
warnings.filterwarnings('ignore')
import os
import database_knotinfo
F=os.path.join(os.path.dirname(database_knotinfo.__file__),'csv_data','knotinfo_data_complete.csv')
def load():
    csv.field_size_limit(10**9)
    r=csv.reader(open(F,newline=''),delimiter='|');hdr=next(r);rows=[x for x in r][1:]
    I={h:i for i,h in enumerate(hdr)}
    return rows,I
def arcs(pd):
    par={}
    def f(x):
        while par.setdefault(x,x)!=x: x=par[x]
        return x
    for a,b,c,d in pd:
        f(a);f(c);par[f(b)]=f(d)
    roots=sorted({f(e) for cr in pd for e in cr})
    idx={r:i for i,r in enumerate(roots)}
    cr=[(idx[f(b)],idx[f(a)],idx[f(c)]) for a,b,c,d in pd]
    return len(roots),cr
def closure(n,cr,seed):
    m=0
    for s in seed: m|=1<<s
    full=(1<<n)-1; ch=True
    while ch:
        ch=False
        for o,u,v in cr:
            if m>>o&1:
                bu=m>>u&1; bv=m>>v&1
                if bu!=bv: m|=(1<<u)|(1<<v); ch=True
    return m==full
def wirt_le(pd,k):
    n,cr=arcs(pd)
    for s in itertools.combinations(range(n),k):
        if closure(n,cr,s): return s
    return None
