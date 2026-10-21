"""Write paper/generated.tex from data/certificates.json, data/still_open.json and KnotInfo."""
import ast, collections, csv, json, os
import database_knotinfo
H = os.path.dirname(os.path.abspath(__file__))
C = json.load(open(os.path.join(H, '..', 'data', 'certificates.json')))['certificates']
S = json.load(open(os.path.join(H, '..', 'data', 'still_open.json')))
p = os.path.join(os.path.dirname(database_knotinfo.__file__), 'csv_data', 'knotinfo_data_complete.csv')
rows = {r['name']: r for r in list(csv.DictReader(open(p, encoding='utf-8', errors='replace'), delimiter='|'))[1:]}
opens = [k for k, r in rows.items() if r['smooth_4d_crosscap_number'].replace(' ', '').startswith('[')]
cert = {c['knot']: c for c in C}
tab = collections.Counter()
for k in opens:
    r = rows[k]
    rg = r['smooth_4d_crosscap_number'].replace(' ', '')
    st = 'settled' if k in cert and cert[k]['closed'] else ('lowered' if k in cert else 'open')
    tab[(int(r['crossing_number']), rg, st)] += 1
keys = sorted({(c, rg) for c, rg, _ in tab})
lines = [r'\begin{tabular}{rlrrrr}', r'\toprule',
         r'crossings & KnotInfo & knots & settled & lowered & open\\', r'\midrule']
tot = [0, 0, 0, 0]
for c, rg in keys:
    v = [tab[(c, rg, s)] for s in ('settled', 'lowered', 'open')]
    n = sum(v)
    tot = [tot[0] + n] + [tot[i + 1] + v[i] for i in range(3)]
    lines.append(r'%d & $%s$ & %d & %d & %d & %d\\' % (c, rg.replace(',', ',\\,'), n, *v))
lines += [r'\midrule', r'all & & %d & %d & %d & %d\\' % tuple(tot), r'\bottomrule', r'\end{tabular}']
closed = [c for c in C if c['closed']]
macros = {
    'ntotal': len(opens), 'ncerts': len(C), 'nclosed': len(closed),
    'nclosedone': sum(c['bound'] == 1 for c in closed), 'nclosedtwo': sum(c['bound'] == 2 for c in closed),
    'nimproved': len(C) - len(closed), 'nchained': sum(c['target_from_this_file'] for c in C),
    'nopen': len(opens) - len(closed),
}
out = [r'\newcommand{\%s}{%s}' % (k, v) for k, v in macros.items()]
out.append(r'\newcommand{\countstable}{%s}' % '\n'.join(lines))
def names(b):
    ks = sorted((c['knot'] for c in closed if c['bound'] == b),
                key=lambda k: (int(k.split('_')[0][:2]), k.split('_')[0][2:], int(k.split('_')[1])))
    return r'\\'.join(k.replace('_', r'\_') for k in ks)
out.append(r'\newcommand{\listone}{%s}' % names(1))
out.append(r'\newcommand{\listtwo}{%s}' % names(2))
st = open(os.path.join(H, 'selftest.tex')).read() if os.path.exists(os.path.join(H, 'selftest.tex')) else r'(see the README)'
out.append(r'\newcommand{\selftesttable}{%s}' % st)
open(os.path.join(H, 'generated.tex'), 'w').write('\n'.join(out) + '\n')
print(macros)
