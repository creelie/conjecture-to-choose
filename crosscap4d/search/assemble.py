import json, glob, collections, sys
sys.argv=['x']
from ki import ROWS
import ast
ok=json.load(open('ok1.json'))
for f in glob.glob('p2v_s*.jsonl'):
    for l in open(f):
        r=json.loads(l)
        if r.get('failed'): continue
        if r['knot'] not in ok or r['bound']<ok[r['knot']]['bound']: ok[r['knot']]=dict(r,chained=True)
def slice_or_known(t):
    if t=='unknot': return True
    rr=ROWS[t]
    return rr['smooth_four_genus'].strip()=='0' or rr['smooth_4d_crosscap_number'].strip().isdigit()
certs=[]
for k,r in ok.items():
    certs.append(dict(knot=k,crossings=int(ROWS[k]['crossing_number']),knotinfo_range=r['range'],diagram=r['pd'],crossing=r['crossing'],smoothing=r['kind'],target=r['target'],bound=r['bound'],closed=bool(r.get('closed')),target_from_this_file=not slice_or_known(r['target'])))
certs.sort(key=lambda c:(c['target_from_this_file'],c['crossings'],c['knot']))
allopen=[k for k,rr in ROWS.items() if rr['smooth_4d_crosscap_number'].replace(' ','').startswith('[')]
still=[dict(knot=k,knotinfo_range=list(ast.literal_eval(ROWS[k]['smooth_4d_crosscap_number'].replace(' ',''))),best_bound=ok[k]['bound'] if k in ok else None) for k in allopen if not (k in ok and ok[k].get('closed'))]
json.dump({'description':'Pinch-move certificates for the smooth nonorientable 4-genus (KnotInfo 2026.10.5 open entries, 11-13 crossings). See ../README.md.','certificates':certs},open(sys.argv[0] and 'certificates.json','w'),indent=0)
json.dump(still,open('still_open.json','w'),indent=0)
C=collections.Counter()
for k in allopen:
    rr=ROWS[k]; rg=rr['smooth_4d_crosscap_number'].replace(' ','')
    st='settled' if k in ok and ok[k].get('closed') else ('lowered' if k in ok else 'open')
    C[(rr['crossing_number'],rg,st)]+=1
print(len(allopen),len(certs),sum(c['closed'] for c in certs),sum(c['target_from_this_file'] for c in certs))
for k,v in sorted(C.items()): print(k,v)
