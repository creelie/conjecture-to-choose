import sys, random, ast, csv, collections
from ki import ROWS, link
from pinch import *
import snappy
HT={}
for n,r in ROWS.items():
    dn=r['dt_name'].replace('_','')
    HT['K'+dn]=n
def gam(name):
    r=ROWS[name]
    if r['smooth_four_genus'].strip()=='0': return 0  # slice => K bounds Mobius after one pinch
    v=r['smooth_4d_crosscap_number'].strip()
    return int(v) if v.isdigit() else None
def ident(L):
    if L is None: return 'unknot'
    if len(L.link_components)!=1: return None
    L.simplify('global')
    if len(L.crossings)==0: return 'unknot'
    if len(L.crossings)>13: return None
    M=L.exterior()
    try:
        ids=M.identify()
    except Exception: return None
    for m in ids:
        nm=m.name()
        if nm in HT: return HT[nm]
        if nm.startswith('K') and nm[1:].replace('a','').replace('n','').isdigit(): pass
    # rolfsen names
    for m in ids:
        nm=m.name()
        if nm in ROWS: return nm
    return None
def bound_from(Lpd):
    best=None
    for i in range(len(Lpd)):
        for kind in (0,1):
            npd,loops=smooth(Lpd,i,kind)
            if loops: continue
            try: L=link_from_pd_unoriented(npd)
            except Exception as e: continue
            if L is not None and len(L.link_components)!=1: continue
            nm=ident(L)
            if nm is None: continue
            g=0 if nm=='unknot' else gam(nm)
            if g is None: continue
            b=1 if g==0 else g+1
            if best is None or b<best[0]: best=(b,i,kind,nm,Lpd)
    return best
if __name__=='__main__':
    names=sys.argv[1].split(','); tries=int(sys.argv[2])
    for n in names:
        lo,hi=ast.literal_eval(ROWS[n]['smooth_4d_crosscap_number'].replace(' ',''))
        K=link(n); best=bound_from(K.PD_code())
        t=0
        while (best is None or best[0]>lo) and t<tries:
            t+=1; K2=K.copy(); K2.backtrack(random.randint(2,10)); K2.simplify('level')
            b=bound_from(K2.PD_code())
            if b and (best is None or b[0]<best[0]): best=b
        print(n,[lo,hi],'->',best[:4] if best else None, 'CLOSED' if best and best[0]==lo and best[0]<hi else '',flush=True)
