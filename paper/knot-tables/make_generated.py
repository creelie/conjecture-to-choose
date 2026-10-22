"""Write bridge-generated.tex and crosscap-generated.tex for knot-tables.tex.

Run paper/make_tables.py and crosscap4d/paper/make_tables.py first; this script copies
their output and gives the bridge-index macros a prefix so that the two sets do not clash.
"""
import os, re, shutil
H = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(H, '..', '..')
RENAME = {'nclosed': 'bclosed', 'nopen': 'bopen', 'ntotal': 'btotal',
          'closedlist': 'bclosedlist', 'openlist': 'bopenlist', 'grouptable': 'bgrouptable'}
src = open(os.path.join(R, 'paper', 'generated.tex')).read()
src = re.sub(r'\\(%s)\b' % '|'.join(RENAME), lambda m: '\\' + RENAME[m.group(1)], src)
open(os.path.join(H, 'bridge-generated.tex'), 'w').write(src)
shutil.copy(os.path.join(R, 'crosscap4d', 'paper', 'generated.tex'), os.path.join(H, 'crosscap-generated.tex'))
