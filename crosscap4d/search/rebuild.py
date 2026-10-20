"""For knots whose certificate did not verify in Regina, look for another pinch with the same
bound that does verify."""
import sys, json, ast, random, signal, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0,'ver')
import verify as V
from ki import ROWS, link
import probe
class TO(Exception): pass
def h(s,f): raise TO()
signal.signal(signal.SIGALRM,h)
def kpd(n): return [tuple(x) for x in ast.literal_eval(ROWS[n]['pd_notation'])]
EXTRA=json.load(open(sys.argv[3])) if len(sys.argv)>3 else {}
orig=probe.gam
probe.gam=lambda n: orig(n) if orig(n) is not None else EXTRA.get(n)
def candidates(Lpd,want):
    for i in range(len(Lpd)):
        for kind in (0,1):
            npd,loops=probe.smooth(Lpd,i,kind)
            if loops: continue
            try: L=probe.link_from_pd_unoriented(npd)
            except Exception: continue
            if L is not None and len(L.link_components)!=1: continue
            nm=probe.ident(L)
            if nm is None: continue
            g=0 if nm=='unknot' else probe.gam(nm)
            if g is None: continue
            if (1 if g==0 else g+1)==want: yield i,kind,nm
def verify_one(Dpd,i,kind,nm,K,secs=15):
    signal.alarm(secs)
    try:
        D=V.orient_pd([tuple(x) for x in Dpd])
        if not V.same_knot(D,kpd(K)): return False
        P=V.orient_pd(V.pinch(D,i,kind))
        return V.is_unknot_diagram(P) if nm=='unknot' else bool(V.same_knot(P,kpd(nm)))
    except TO: return False
    finally: signal.alarm(0)
todo=[json.loads(l) for l in open(sys.argv[1])]
import os
done=set()
for f in [x for x in os.listdir('.') if x.startswith(os.environ.get('PFX','rebuilt'))]:
    done|={json.loads(l)['knot'] for l in open(f)}
todo=[r for k,r in enumerate(todo) if r['knot'] not in done and k%int(os.environ.get('NS','1'))==int(os.environ.get('SH','0'))]
out=open(sys.argv[2],'a')
for r in todo:
    K=r['knot']; want=r['bound']; random.seed(K)
    found=None; L0=link(K)
    for t in range(25):
        L=L0.copy()
        if t: L.backtrack(random.randint(2,12)); L.simplify(random.choice(['level','basic']))
        pd=L.PD_code()
        for i,kind,nm in candidates(pd,want):
            if verify_one(pd,i,kind,nm,K):
                found=dict(r,crossing=i,kind=kind,target=nm,pd=[list(x) for x in pd]); break
        if found: break
    out.write(json.dumps(found if found else dict(r,failed=True))+'\n'); out.flush()
