import sys, random, ast, json, warnings
warnings.filterwarnings('ignore')
from multiprocessing import Pool
from ki import ROWS, link
import probe
def work(n):
    random.seed(hash(n)&0xffff)
    lo,hi=ast.literal_eval(ROWS[n]['smooth_4d_crosscap_number'].replace(' ',''))
    K=link(n)
    try: best=probe.bound_from(K.PD_code())
    except Exception as e: best=None
    t=0
    while (best is None or best[0]>lo) and t<8:
        t+=1; K2=K.copy(); K2.backtrack(random.randint(2,10)); K2.simplify('level')
        try: b=probe.bound_from(K2.PD_code())
        except Exception: continue
        if b and (best is None or b[0]<best[0]): best=b
    rec={'knot':n,'range':[lo,hi]}
    if best and best[0]<hi:
        rec.update(bound=best[0],crossing=best[1],kind=best[2],target=best[3],pd=[list(x) for x in best[4]],closed=best[0]==lo)
    return rec
if __name__=='__main__':
    names=[n for n,r in ROWS.items() if r['smooth_4d_crosscap_number'].replace(' ','').startswith('[')]
    print(len(names),file=sys.stderr)
    with Pool(4) as P, open('results.jsonl','w') as f:
        for i,rec in enumerate(P.imap_unordered(work,names,chunksize=4)):
            f.write(json.dumps(rec)+'\n'); f.flush()
