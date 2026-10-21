"""Third pass: every pinch of the KnotInfo diagram and of random diagrams of each open knot,
kept only when the Regina tests of ../verify/verify.py (with the seeded complement test of
certify.py) accept it. Usage: python3 run3.py NDIAG OUT.jsonl; run3b.py also takes earlier
outputs and uses the knots they settle as targets."""
import sys, json, ast, random, signal, time, warnings, os
warnings.filterwarnings('ignore')
sys.path.insert(0,'../search'); sys.path.insert(0,'../verify'); sys.path.insert(0,'.')
from multiprocessing import Pool
import verify as V, certify as C
from ki import ROWS, link
import probe
class TO(Exception): pass
def h(s,f): raise TO()
def kpd(n): return [tuple(x) for x in ast.literal_eval(ROWS[n]['pd_notation'])]
def same(a,b): return bool(V.same_knot(a,b,attempts=1)) or C.cloud_same(a,b)
def cands(pd,want):
    for i in range(len(pd)):
        for kind in (0,1):
            npd,loops=probe.smooth(pd,i,kind)
            if loops: continue
            try: L=probe.link_from_pd_unoriented(npd)
            except Exception: continue
            if L is not None and len(L.link_components)!=1: continue
            nm=probe.ident(L)
            if nm is None: continue
            g=0 if nm=='unknot' else probe.gam(nm)
            if g is None: continue
            if (1 if g==0 else g+1)==want: yield i,kind,nm
def work(args):
    K,lo,hi,ndiag=args; signal.signal(signal.SIGALRM,h); random.seed(K)
    L0=link(K); tried=0
    for t in range(ndiag):
        L=L0.copy()
        if t: L.backtrack(random.randint(2,12)); L.simplify(random.choice(['level','basic']))
        pd=L.PD_code()
        for i,kind,nm in cands(pd,lo):
            tried+=1; signal.alarm(90)
            try:
                D=V.orient_pd([tuple(x) for x in pd])
                if not same(D,kpd(K)): continue
                P=V.orient_pd(V.smooth(D,i,kind))
                if P is None: continue
                ok=V.is_unknot(P) if nm=='unknot' else same(P,kpd(nm))
                if ok:
                    return dict(knot=K,crossings=int(ROWS[K]['crossing_number']),knotinfo_range=[lo,hi],
                        diagram=[list(x) for x in pd],crossing=i,smoothing=kind,target=nm,bound=lo,closed=True,diag_index=t)
            except TO: pass
            finally: signal.alarm(0)
    return dict(knot=K,failed=True,candidates=tried)
if __name__=='__main__':
    ndiag=int(sys.argv[1]); out=sys.argv[2]
    so=json.load(open('../data/still_open.json'))
    done=set()
    if os.path.exists(out): done={json.loads(l)['knot'] for l in open(out)}
    todo=[(x['knot'],*x['knotinfo_range'],ndiag) for x in so if x['knot'] not in done]
    t=time.time(); n=0; c=0
    with Pool(4) as P, open(out,'a') as f:
        for r in P.imap_unordered(work,todo,chunksize=1):
            f.write(json.dumps(r)+'\n'); f.flush(); n+=1; c+=not r.get('failed')
            if n%50==0: print(n,c,round(time.time()-t),flush=True)
    print('DONE',n,c,round(time.time()-t),flush=True)
