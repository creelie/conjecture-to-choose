#!/usr/bin/env python3
"""Apply the Donaldson obstructions of obstruct.py to every alternating knot of
data/still_open.json and write those that raise the KnotInfo lower bound to
data/lower_bounds.json."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import obstruct as O
import verify as V

def main():
    R = V.knotinfo_rows()
    S = json.load(open(os.path.join(HERE, '..', 'data', 'still_open.json')))
    out = []
    for e in S:
        k = e['knot']
        if R[k]['alternating'] != 'Y':
            continue
        lo, hi = V.ki_range(R, k)
        a = O.analyse(V.ki_pd(R, k), int(R[k]['arf_invariant']), int(R[k]['determinant']))
        if a['bound'] is not None and a['bound'] > lo:
            out.append(dict(knot=k, knotinfo_range=[lo, hi], **a))
            print(k, a['theorem'], a['bound'], flush=True)
    json.dump({'source': 'KnotInfo 2026.10.5 diagrams; Jabuka-Kelly Theorems 2.10-2.12',
               'lower_bounds': out},
              open(os.path.join(HERE, '..', 'data', 'lower_bounds.json'), 'w'), indent=1)
    print(len(out), 'lower bounds raised')

if __name__ == '__main__':
    main()
