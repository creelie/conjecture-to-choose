"""Collect the search results into data/certificates.json (one certificate per knot).
Usage: python3 search/make_certificates.py RESULTS_DIR OUT.json"""
import ast, glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wirt import load, arcs, wirt_le
from convert import mats_for, uf_labels
res, out = sys.argv[1], sys.argv[2]
rows, I = load()
PD = {x[I['name']]: ast.literal_eval(x[I['pd_notation']]) for x in rows if x[I['bridge_index']] == '[3,4]'}
found = {}
def take(fn, fun):
    p = os.path.join(res, fn)
    if os.path.exists(p):
        for k, v in json.load(open(p)).items():
            c = fun(v)
            if c and k not in found: found[k] = c
take('sp4_3_1.json', lambda v: v['cert'] and ('sp', 3, v['cert'], None, 'Sp(4,3) transvections'))
take('r5_1.json', lambda v: v['cert'] and ('sp', 5, v['cert'], None, 'Sp(4,5) transvections'))
take('orth.json', lambda v: v['cert'] and ('o', 5, v['cert'], tuple(v['diag']), 'O(4,5) reflections'))
for fn in sorted(glob.glob(os.path.join(res, 'g[0-9]*.json'))):
    take(os.path.basename(fn), lambda v: ('sp-gram', v['q'], v['colors'], v['W'], f"Sp(4,{v['q']}) transvections"))
for fn in sorted(glob.glob(os.path.join(res, 'og[0-9]*.json'))):
    take(os.path.basename(fn), lambda v: ('o-gram', v['q'], v['colors'], v['B'], f"O(4,{v['q']}) reflections"))
for fn in sorted(glob.glob(os.path.join(res, 'gl*.json'))):
    take(os.path.basename(fn), lambda v: ('gl', v['q'], None, (v['V'], v['F']), f"GL(4,{v['q']}) pseudo-reflections"))
certs = []
for name in sorted(found, key=lambda s: (s.split('_')[0], int(s.split('_')[1]))):
    kind, q, data, extra, group = found[name]
    pd = PD[name]
    m = mats_for(pd, data, kind, q, extra)
    n, cr = arcs(pd)
    seeds = wirt_le(pd, 4)
    lab = uf_labels(pd)
    rep = {}
    for e in sorted(lab):
        rep.setdefault(lab[e], e)
    certs.append({'name': name, 'pd': pd, 'field': q, 'group': group,
                  'matrices': [m[e] for e in range(1, 2 * len(pd) + 1)],
                  'wirtinger_seeds': [rep[s] for s in seeds]})
json.dump(certs, open(out, 'w'), separators=(',', ':'))
open_names = sorted(set(PD) - set(found), key=lambda s: (s.split('_')[0], int(s.split('_')[1])))
json.dump(open_names, open(os.path.join(os.path.dirname(out), 'still_open.json'), 'w'), indent=0)
from collections import Counter
print(len(certs), 'certificates;', len(open_names), 'still open;', dict(Counter(c['group'] for c in certs)))
