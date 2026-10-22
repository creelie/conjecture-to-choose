"""Write paper/generated.tex from data/certificates.json, data/still_open.json and KnotInfo."""
import ast, collections, csv, json, os
import database_knotinfo
H = os.path.dirname(os.path.abspath(__file__))
C = json.load(open(os.path.join(H, '..', 'data', 'certificates.json')))['certificates']
S = json.load(open(os.path.join(H, '..', 'data', 'still_open.json')))
p = os.path.join(os.path.dirname(database_knotinfo.__file__), 'csv_data', 'knotinfo_data_complete.csv')
rows = {r['name']: r for r in list(csv.DictReader(open(p, encoding='utf-8', errors='replace'), delimiter='|'))[1:]}
opens = [k for k, r in rows.items() if r['smooth_4d_crosscap_number'].replace(' ', '').startswith('[')]
L = {d['knot']: d for d in json.load(open(os.path.join(H, '..', 'data', 'lower_bounds.json')))['lower_bounds']}
cert = {c['knot']: c for c in C}
tab = collections.Counter()
how = collections.Counter()
final = {}
for k in opens:
    r = rows[k]
    rg = r['smooth_4d_crosscap_number'].replace(' ', '')
    lo, hi = ast.literal_eval(rg)
    lo2 = max(lo, L[k]['bound']) if k in L else lo
    hi2 = min(hi, cert[k]['bound']) if k in cert else hi
    final[k] = (lo2, hi2)
    if lo2 == hi2:
        st = 'settled'
        how[('pinch' if lo2 == lo else ('lower' if hi2 == hi else 'both'), lo2)] += 1
    else:
        st = 'lowered' if (lo2, hi2) != (lo, hi) else 'open'
    tab[(int(r['crossing_number']), rg, st)] += 1
keys = sorted({(c, rg) for c, rg, _ in tab})
lines = [r'\begin{tabular}{rlrrrr}', r'\toprule',
         r'crossings & KnotInfo & knots & settled & narrowed & open\\', r'\midrule']
tot = [0, 0, 0, 0]
for c, rg in keys:
    v = [tab[(c, rg, s)] for s in ('settled', 'lowered', 'open')]
    n = sum(v)
    tot = [tot[0] + n] + [tot[i + 1] + v[i] for i in range(3)]
    lines.append(r'%d & $%s$ & %d & %d & %d & %d\\' % (c, rg.replace(',', ',\\,'), n, *v))
lines += [r'\midrule', r'all & & %d & %d & %d & %d\\' % tuple(tot), r'\bottomrule', r'\end{tabular}']
closed = [c for c in C if c['closed']]
settled = [k for k in opens if final[k][0] == final[k][1]]
macros = {
    'ntotal': len(opens), 'ncerts': len(C), 'nclosed': len(closed),
    'nclosedone': sum(c['bound'] == 1 for c in closed), 'nclosedtwo': sum(c['bound'] == 2 for c in closed),
    'nimproved': len(C) - len(closed), 'nchained': sum(c['target_from_this_file'] for c in C),
    'nlower': len(L), 'nlowertwo': sum(d['bound'] == 2 for d in L.values()),
    'nlowerthree': sum(d['bound'] == 3 for d in L.values()),
    'nlowerten': sum(d['theorem'] == '2.10' for d in L.values()),
    'nlowereleven': sum(d['theorem'] == '2.11' for d in L.values()),
    'nlowertwelve': sum(d['theorem'] == '2.12' for d in L.values()),
    'nsettled': len(settled), 'nsettledpinch': sum(v for (a, b), v in how.items() if a == 'pinch'),
    'nsettledlower': sum(v for (a, b), v in how.items() if a == 'lower'),
    'nsettledboth': sum(v for (a, b), v in how.items() if a == 'both'),
    'nsettledone': sum(final[k][0] == 1 for k in settled), 'nsettledtwo': sum(final[k][0] == 2 for k in settled),
    'nsettledthree': sum(final[k][0] == 3 for k in settled),
    'nnarrowed': sum(1 for k in opens if final[k][0] < final[k][1] and final[k] != tuple(ast.literal_eval(rows[k]['smooth_4d_crosscap_number'].replace(' ', '')))),
    'nopen': len(opens) - len(settled),
}
out = [r'\newcommand{\%s}{%s}' % (k, v) for k, v in macros.items()]
out.append(r'\newcommand{\countstable}{%s}' % '\n'.join(lines))
def names(b):
    ks = sorted((k for k in settled if final[k][0] == b),
                key=lambda k: (int(k.split('_')[0][:2]), k.split('_')[0][2:], int(k.split('_')[1])))
    return r'\\'.join(k.replace('_', r'\_') for k in ks)
out.append(r'\newcommand{\listone}{%s}' % names(1))
out.append(r'\newcommand{\listtwo}{%s}' % names(2))
out.append(r'\newcommand{\listthree}{%s}' % names(3))
st = open(os.path.join(H, 'selftest.tex')).read() if os.path.exists(os.path.join(H, 'selftest.tex')) else r'(see the README)'
out.append(r'\newcommand{\selftesttable}{%s}' % st)
open(os.path.join(H, 'generated.tex'), 'w').write('\n'.join(out) + '\n')
print(macros)
