import sys, random, ast, json, warnings
warnings.filterwarnings('ignore')
from multiprocessing import Pool
from ki import ROWS, link
import probe
R=[json.loads(l) for l in open('results.jsonl')]
NEW={r['knot']:r['bound'] for r in R if r.get('closed')}
orig=probe.gam
def gam(name):
    g=orig(name)
    if g is None and name in NEW: return NEW[name]
    return g
probe.gam=gam
def work(r):
    n=r['knot']; random.seed(hash(n)&0xffff ^ 77)
    lo,hi=r['range']; cur=r.get('bound',hi)
    K=link(n); best=None
    for t in range(12):
        K2=K.copy()
        if t: K2.backtrack(random.randint(2,14)); K2.simplify(random.choice(['level','basic']))
        try: b=probe.bound_from(K2.PD_code())
        except Exception: continue
        if b and (best is None or b[0]<best[0]): best=b
        if best and best[0]==lo: break
    rec=dict(r)
    if best and best[0]<cur:
        rec.update(bound=best[0],crossing=best[1],kind=best[2],target=best[3],pd=[list(x) for x in best[4]],closed=best[0]==lo,pass2=True)
    return rec
if __name__=='__main__':
    todo=[r for r in R if not r.get('closed')]
    with Pool(2) as P, open('results2.jsonl','w') as f:
        for rec in P.imap_unordered(work,todo,chunksize=2):
            f.write(json.dumps(rec)+'\n'); f.flush()
