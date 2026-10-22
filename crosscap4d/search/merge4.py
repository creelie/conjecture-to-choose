"""Merge verified pinch certificates (a new_certs.json written after verify.check) and the
lower bounds of data/lower_bounds.json into data/certificates.json and data/still_open.json.

usage: python3 search/merge4.py new_certs.json"""
import json, os, sys
H = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(H, '..', 'verify'))
import verify as V
D = os.path.join(H, '..', 'data')
R = V.knotinfo_rows()
cf = json.load(open(os.path.join(D, 'certificates.json')))
certs = {c['knot']: c for c in cf['certificates']}
for c in json.load(open(sys.argv[1]))['ok']:
    if c['knot'] not in certs or c['bound'] < certs[c['knot']]['bound']:
        certs[c['knot']] = c
cl = sorted(certs.values(), key=lambda c: (c['target_from_this_file'], c['crossings'], c['knot']))
cf['certificates'] = cl
json.dump(cf, open(os.path.join(D, 'certificates.json'), 'w'), indent=0)
lower = {d['knot']: d['bound'] for d in
         json.load(open(os.path.join(D, 'lower_bounds.json')))['lower_bounds']}
old = {e['knot']: e for e in json.load(open(os.path.join(D, 'still_open.json')))}
still = []
for k, r in R.items():
    if not r['smooth_4d_crosscap_number'].replace(' ', '').startswith('['):
        continue
    lo, hi = V.ki_range(R, k)
    lo2 = max(lo, lower.get(k, lo))
    hi2 = min(hi, certs[k]['bound']) if k in certs else hi
    if lo2 == hi2:
        continue
    e = dict(knot=k, knotinfo_range=[lo, hi], interval=[lo2, hi2],
             verified_bound=certs[k]['bound'] if k in certs else None,
             lower_bound=lower.get(k))
    u = old.get(k, {}).get('unverified_candidate')
    if u and u['bound'] < hi2:
        e['unverified_candidate'] = u
    still.append(e)
json.dump(still, open(os.path.join(D, 'still_open.json'), 'w'), indent=0)
print(len(cl), 'certificates;', len(still), 'knots open')
