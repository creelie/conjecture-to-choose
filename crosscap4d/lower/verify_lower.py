#!/usr/bin/env python3
"""Check data/lower_bounds.json.

For every record it recomputes, from the KnotInfo diagram, Arf invariant and determinant:
  - the signature by Gordon-Litherland from both checkerboard colourings (they must agree,
    and |sigma| must equal KnotInfo's |sigma|);
  - the definite Goeritz forms and the obstruction of Jabuka and Kelly, which must give the
    stored bound, using a basis order shuffled with a fixed seed (a different search order
    from the one that produced the file).

With --selftest it also runs the obstruction on every alternating knot with at most eleven
crossings whose gamma_4 KnotInfo knows: the obstruction must never exceed the known value,
and the variant with the opposite sign convention for sigma must contradict known values
(so the sign convention is tested, not assumed). With --certificates it runs the obstruction
on every alternating knot of data/certificates.json: it must never exceed the upper bound the
pinch certificate proves.
"""
import json, os, random, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import obstruct as O, embed as E
import verify as V


def check_file(R):
    data = json.load(open(os.path.join(HERE, '..', 'data', 'lower_bounds.json')))['lower_bounds']
    rnd = random.Random(2026)
    E.order_basis = lambda P: rnd.sample(range(len(P)), len(P))
    bad = []
    for d in data:
        k = d['knot']
        pd = V.ki_pd(R, k)
        sigma, _, _ = O.forms(pd)
        if abs(sigma) != abs(int(R[k]['signature'])):
            bad.append((k, 'signature'))
            continue
        a = O.analyse(pd, int(R[k]['arf_invariant']), int(R[k]['determinant']))
        lo, hi = V.ki_range(R, k)
        if a['bound'] != d['bound'] or a['theorem'] != d['theorem'] or not lo < a['bound'] <= hi:
            bad.append((k, d['bound'], a['bound']))
    print(f'{len(data) - len(bad)} of {len(data)} lower bounds confirmed', flush=True)
    return bad


def selftest(R):
    false_alarm = swapped_alarm = tested = 0
    for k, r in R.items():
        if r['alternating'] != 'Y' or k == '0_1' or int(r['crossing_number']) > 11:
            continue
        try:
            lo, hi = V.ki_range(R, k)
        except ValueError:
            continue
        if lo != hi:
            continue
        pd = V.ki_pd(R, k)
        arf, det = int(r['arf_invariant']), int(r['determinant'])
        tested += 1
        b = O.analyse(pd, arf, det, budget=2_000_000)['bound']
        if b is not None and b > lo:
            false_alarm += 1
            print('FALSE ALARM', k, lo, b)
        sigma, Pp, Pm = O.forms(pd)
        s8 = (-sigma + 4 * arf) % 8
        if lo == 1 and s8 in (2, 6) and O.blocked(Pm if s8 == 2 else Pp, det, 2_000_000)[0]:
            swapped_alarm += 1
    print(f'selftest: {tested} knots with known gamma_4; obstruction above the known value: '
          f'{false_alarm}; with the opposite sign convention: {swapped_alarm}')
    return false_alarm == 0 and swapped_alarm > 0


def against_certificates(R):
    C = json.load(open(os.path.join(HERE, '..', 'data', 'certificates.json')))['certificates']
    n = fired = 0
    bad = []
    for c in C:
        k = c['knot']
        if R[k]['alternating'] != 'Y':
            continue
        n += 1
        b = O.analyse(V.ki_pd(R, k), int(R[k]['arf_invariant']), int(R[k]['determinant']),
                      budget=2_000_000)['bound']
        if b is not None:
            fired += 1
            if b > c['bound']:
                bad.append(k)
                print('CONFLICT', k, c['bound'], b)
    print(f'certificates: {n} alternating knots, obstruction defined for {fired}, '
          f'above the pinch bound for {len(bad)}')
    return not bad


if __name__ == '__main__':
    R = V.knotinfo_rows()
    bad = check_file(R)
    ok = not bad
    if bad:
        print('FAILED', bad)
    if '--selftest' in sys.argv:
        ok = selftest(R) and ok
    if '--certificates' in sys.argv:
        ok = against_certificates(R) and ok
    sys.exit(0 if ok else 1)
