"""Closed 3-braids in Murasugi normal form; identify against the open 13-crossing knots.
A knot that is a closed 3-braid has bridge index <= 3."""
import sys, json, ast, itertools, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0,'.')
import snappy
from wirt import load
rows,I=load(); S=set(json.load(open('../data/still_open.json')))
vol={}
for x in rows:
    if x[I['name']] in S:
        M=snappy.Link(ast.literal_eval(x[I['pd_notation']])).exterior()
        vol.setdefault(round(float(M.volume()),6),[]).append(x[I['name']])
print('targets',len(S),'distinct vols',len(vol),flush=True)
def comps(total):
    if total==0: yield (); return
    for k in range(1,total+1):
        for r in comps(total-k): yield (k,)+r
def necklaces(smax):
    seen=set()
    for s in range(2,smax+1):
        for c in comps(s):
            if len(c)%2: continue
            rots=[c[i:]+c[:i] for i in range(0,len(c),2)]
            key=min(rots)
            if key in seen: continue
            seen.add(key); yield key
Delta2=[1,2,1,1,2,1]
hits={}; tried=0
def test(word,label):
    global tried
    tried+=1
    try:
        L=snappy.Link(braid_closure=word)
        if len(L.link_components)!=1: return
        M=L.exterior(); v=round(float(M.volume()),6)
    except Exception: return
    for vv in (v-1e-6,v,v+1e-6):
        if round(vv,6) in vol:
            for ident in M.identify():
                nm=str(ident).split('(')[0]
                if nm.startswith('K13'):
                    k=nm[1:3]+nm[3]+'_'+nm[4:]
                    if k in S and k not in hits:
                        hits[k]=word; print('HIT',k,label,word,flush=True)
            break
SMAX=int(sys.argv[1]); DMAX=int(sys.argv[2])
for c in necklaces(SMAX):
    base=[]
    for i,e in enumerate(c): base+= [-1]*e if i%2==0 else [2]*e
    for d in range(-DMAX,DMAX+1):
        if d!=0 and len(base)+4*abs(d)>SMAX+4: continue
        w=(Delta2*d if d>0 else [-x for x in Delta2[::-1]]*(-d))+base
        test(w,(c,d))
# exceptional classes: Delta^{2d} sigma2^m, Delta^{2d} sigma1^m sigma2^-1 (m in -1..-3)
for d in range(-DMAX,DMAX+1):
    D=(Delta2*d if d>0 else [-x for x in Delta2[::-1]]*(-d))
    for m in range(-20,21): test(D+[2]*m if m>=0 else D+[-2]*(-m),('s2',m,d))
    for m in (-1,-2,-3): test(D+[1]*(-m)*-1+[-2] if False else D+[-1]*(-m)+[-2],('s1s2',m,d))
print('tried',tried,'hits',len(hits))
json.dump(hits,open('hits_%d_%d.json'%(SMAX,DMAX),'w'),indent=1)
