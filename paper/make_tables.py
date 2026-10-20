"""Write paper/generated.tex (counts and knot lists) from data/certificates.json."""
import json, os
from collections import Counter
here = os.path.dirname(os.path.abspath(__file__))
certs = json.load(open(os.path.join(here, '..', 'data', 'certificates.json')))
still = json.load(open(os.path.join(here, '..', 'data', 'still_open.json')))
cnt = Counter(c['group'] for c in certs)
def tex_name(s):
    a, b = s.split('_')
    return f'$13\\mathrm{{{a[-1]}}}_{{{b}}}$'
lines = [f'\\newcommand{{\\nclosed}}{{{len(certs)}}}', f'\\newcommand{{\\nopen}}{{{len(still)}}}',
         f'\\newcommand{{\\ntotal}}{{{len(certs) + len(still)}}}']
rows = []
for g in sorted(cnt, key=lambda g: (g.split('(')[0], int(g.split(',')[1].split(')')[0]))):
    grp, rest = g.split(' ', 1)
    G, args = grp.split('(')
    n, q = args.rstrip(')').split(',')
    gname = {'Sp': '\\Sp', 'O': '\\O', 'GL': '\\GL'}[G]
    rows.append(f'${gname}_{n}(\\F_{{{q}}})$ & {rest} & {cnt[g]} \\\\')
lines.append('\\newcommand{\\grouptable}{' + '\n'.join(rows) + '}')
lines.append('\\newcommand{\\closedlist}{' + ', '.join(tex_name(c['name']) for c in certs) + '}')
lines.append('\\newcommand{\\openlist}{' + ', '.join(tex_name(s) for s in still) + '}')
open(os.path.join(here, 'generated.tex'), 'w').write('\n'.join(lines) + '\n')
print(len(certs), len(still), dict(cnt))
