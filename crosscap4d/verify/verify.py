#!/usr/bin/env python3
"""Independent verifier for the pinch-move certificates in ../data/certificates.json.

It uses Regina (pip install regina) for every topological step and the KnotInfo database
(pip install database_knotinfo) for the knot diagrams and the published values it takes as
input. It does not use SnapPy, which the search used.

For each certificate it checks:
  1. the stored diagram D is a diagram of the knot K (Reidemeister moves to the KnotInfo
     diagram, or a combinatorial isomorphism of triangulated complements);
  2. the non-orientable smoothing of the named crossing of D is a one-component diagram D';
  3. D' is the target knot T up to mirror image (same two tests) or the unknot (Regina's
     solid torus recognition);
  4. the bound: gamma4(K) <= 1 if T is slice or the unknot, else gamma4(K) <= gamma4(T) + 1,
     with the slice status and gamma4(T) read from KnotInfo, or from an earlier certificate
     of this file that settled T;
  5. for certificates marked closed, the bound equals the lower end of the KnotInfo range.

Usage:
  python3 verify.py                 # check every certificate
  python3 verify.py --selftest      # also check that corrupted certificates are rejected
"""
import ast, csv, json, os, sys, time
import regina

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, '..', 'data', 'certificates.json')


# ---------- KnotInfo ----------

def knotinfo_rows():
    import database_knotinfo
    p = os.path.join(os.path.dirname(database_knotinfo.__file__), 'csv_data',
                     'knotinfo_data_complete.csv')
    rows = list(csv.DictReader(open(p, encoding='utf-8', errors='replace'), delimiter='|'))[1:]
    return {r['name']: r for r in rows}


def ki_pd(rows, name):
    return [tuple(x) for x in ast.literal_eval(rows[name]['pd_notation'])]


def ki_range(rows, name):
    v = rows[name]['smooth_4d_crosscap_number'].replace(' ', '')
    if v.startswith('['):
        return list(ast.literal_eval(v))
    return [int(v), int(v)]


def ki_value(rows, name):
    """(slice?, gamma4 or None) from KnotInfo."""
    r = rows[name]
    if r['smooth_four_genus'].strip() == '0':
        return True, 1
    v = r['smooth_4d_crosscap_number'].strip()
    return False, (int(v) if v.isdigit() else None)


# ---------- diagrams ----------

def orient_pd(cross):
    """Unoriented PD tuples (a,b,c,d), counterclockwise, under strand a-c, over strand b-d.
    Returns an oriented PD code with labels 1..2n (first entry the incoming under strand),
    or None when the diagram has more than one component."""
    n = len(cross)
    if n == 0:
        return []
    occ = {}
    for i, t in enumerate(cross):
        for j, l in enumerate(t):
            occ.setdefault(l, []).append((i, j))
    if any(len(v) != 2 for v in occ.values()):
        raise ValueError('malformed PD code')
    start = (0, 0)
    i, j = start
    order, seen = [], set()
    while True:
        order.append((i, j))
        seen.add((i, j))
        out = (j + 2) % 4
        (k, m), = [e for e in occ[cross[i][out]] if e != (i, out)]
        i, j = k, m
        if (i, j) == start:
            break
        if (i, j) in seen:
            raise ValueError('malformed PD code')
    if len(order) != 2 * n:
        return None
    N = 2 * n
    lab = {}
    for t, (i, j) in enumerate(order):
        lab[(i, j)] = t if t > 0 else N
        lab[(i, (j + 2) % 4)] = t + 1
    entered = set(order)
    pd = []
    for i in range(n):
        new = [lab[(i, j)] for j in range(4)]
        pd.append(tuple(new) if (i, 0) in entered else (new[2], new[3], new[0], new[1]))
    return pd


def smooth(cross, idx, kind):
    """Remove crossing idx, joining strands (a,b),(c,d) if kind == 0, (a,d),(b,c) if kind == 1."""
    a, b, c, d = cross[idx]
    rest = [list(t) for k, t in enumerate(cross) if k != idx]
    pairs = [(a, b), (c, d)] if kind == 0 else [(a, d), (b, c)]
    for p in range(2):
        x, y = pairs[p]
        if x == y:
            raise ValueError('smoothing leaves a free circle')
        for t in rest:
            for q in range(4):
                if t[q] == y:
                    t[q] = x
        pairs = [(u if u != y else x, v if v != y else x) for u, v in pairs]
    return [tuple(t) for t in rest]


# ---------- identification ----------

def complement(pd):
    T = regina.Link.fromPD(pd).complement()
    T.simplify()
    return T


def isosig_cloud(T, height=1):
    sigs = {T.isoSig()}
    T.retriangulate(height, 1, lambda sig, tri: sigs.add(sig) or False)
    return sigs


def minimal_class(L, cap=400):
    n = L.size()
    seen = {L.sig(True, True, True)}
    frontier = [regina.Link(L)]
    while frontier and len(seen) < cap:
        nxt = []
        for X in frontier:
            def act(sig, lk):
                if lk.size() == n:
                    s = lk.sig(True, True, True)
                    if s not in seen:
                        seen.add(s)
                        nxt.append(regina.Link(lk))
                return False
            X.rewrite(1, 1, act)
        frontier = nxt
    return seen


_cache = {}


def same_knot(pd1, pd2, attempts=4):
    """'isotopy', 'complement' or None (no proof found). Regina's simplification is randomised;
    each attempt starts from a fixed seed, so the outcome is reproducible, and any successful
    attempt is a proof."""
    for k in range(attempts):
        regina.RandomEngine.reseedWithDefault()
        for _ in range(997 * k):
            regina.RandomEngine.rand(1000)
        m = _same_knot_once(pd1, pd2)
        if m:
            return m
    return None


def _same_knot_once(pd1, pd2):
    key = tuple(pd2)
    if key not in _cache:
        B = regina.Link.fromPD(pd2)
        B.simplify()
        _cache[key] = {'B': B, 'cls': None, 'tri': None, 'cloud': None}
    tg = _cache[key]
    B = tg['B']
    A = regina.Link.fromPD(pd1)
    A.simplify()
    while A.size() > B.size() and A.simplifyExhaustive(1):
        pass
    if A.size() == B.size():
        if A.sig(True, True, True) == B.sig(True, True, True):
            return 'isotopy'
        if tg['cls'] is None:
            tg['cls'] = minimal_class(B)
        if minimal_class(A) & tg['cls']:
            return 'isotopy'
    T1 = complement(pd1)
    if tg['tri'] is None:
        tg['tri'] = complement(pd2)
    if T1.isIsomorphicTo(tg['tri']) is not None:
        return 'complement'
    if tg['cloud'] is None:
        tg['cloud'] = isosig_cloud(tg['tri'])
    if isosig_cloud(T1) & tg['cloud']:
        return 'complement'
    return None


def is_unknot(pd):
    if len(pd) == 0:
        return True
    L = regina.Link.fromPD(pd)
    L.simplify()
    if L.size() == 0:
        return True
    return complement(pd).isSolidTorus()


# ---------- certificates ----------

def check(cert, rows, settled):
    """Return None if the certificate is valid, else the reason it fails."""
    K = cert['knot']
    D = orient_pd([tuple(x) for x in cert['diagram']])
    if D is None:
        return 'diagram is not a knot diagram'
    if not same_knot(D, ki_pd(rows, K)):
        return 'diagram not identified with the KnotInfo knot'
    P = orient_pd(smooth(D, cert['crossing'], cert['smoothing']))
    if P is None:
        return 'smoothing is orientable (two components), not a pinch'
    T = cert['target']
    if T == 'unknot':
        if not is_unknot(P):
            return 'pinched diagram is not the unknot'
        bound = 1
    else:
        if not same_knot(P, ki_pd(rows, T)):
            return 'pinched diagram not identified with the target'
        sl, g = ki_value(rows, T)
        if g is None:
            g = settled.get(T)
        if g is None:
            return 'gamma4 of the target is not known'
        bound = 1 if sl else g + 1
    if bound != cert['bound']:
        return 'bound %d does not follow (computed %d)' % (cert['bound'], bound)
    lo, hi = ki_range(rows, K)
    if cert['knotinfo_range'] != [lo, hi]:
        return 'KnotInfo range differs from the certificate'
    if not bound < hi:
        return 'bound does not improve KnotInfo'
    if cert['closed'] != (bound == lo):
        return 'closed flag inconsistent'
    return None


def _child(c, rows, settled, conn):
    try:
        conn.send(check(c, rows, settled))
    except Exception as e:
        conn.send('error: %s' % e)
    conn.close()


def _start(c, rows, settled):
    import multiprocessing as mp
    a, b = mp.Pipe(False)
    p = mp.get_context('fork').Process(target=_child, args=(c, rows, settled, b))
    p.start()
    b.close()
    return p, a


def _finish(p, a, timed_out):
    if timed_out:
        p.kill()
        p.join()
        return None, True
    p.join()
    return (a.recv() if a.poll() else 'no result'), False


def check_limited(c, rows, settled, seconds):
    """Run check() in a forked process; a certificate whose check exceeds the time limit
    counts as failed."""
    p, a = _start(c, rows, settled)
    p.join(seconds)
    why, to = _finish(p, a, p.is_alive())
    return 'time limit of %ds exceeded' % seconds if to else why


def run(certs, rows, verbose=True, seconds=120, jobs=4):
    """Check the certificates, each in its own forked process, jobs at a time (no threads).
    A certificate whose target is settled by an earlier certificate of this file is checked
    after all the others."""
    first = [c for c in certs if not c.get('target_from_this_file')]
    later = [c for c in certs if c.get('target_from_this_file')]
    settled, bad = {}, []
    t0 = time.time()
    done = 0
    for batch in (first, later):
        snap = dict(settled)
        results = [None] * len(batch)
        queue = list(range(len(batch)))
        running = {}
        while queue or running:
            while queue and len(running) < jobs:
                i = queue.pop(0)
                running[i] = _start(batch[i], rows, snap) + (time.time(),)
            time.sleep(0.01)
            for i in list(running):
                p, a, t = running[i]
                over = time.time() - t > seconds
                if over or not p.is_alive() or a.poll():
                    why, to = _finish(p, a, over and p.is_alive() and not a.poll())
                    results[i] = 'time limit of %ds exceeded' % seconds if to else why
                    del running[i]
                    done += 1
                    if verbose and done % 500 == 0:
                        print('  %d checked, %.0fs' % (done, time.time() - t0), flush=True)
        for c, why in zip(batch, results):
            if why:
                bad.append((c['knot'], why))
            elif c['closed']:
                settled[c['knot']] = c['bound']
    return settled, bad


def main():
    rows = knotinfo_rows()
    certs = json.load(open(DATA))['certificates']
    settled, bad = run(certs, rows)
    print('%d certificates, %d failed' % (len(certs), len(bad)))
    for b in bad:
        print('  FAIL', *b)
    failed = {k for k, _ in bad}
    lowered = sum(1 for c in certs if not c['closed'] and c['knot'] not in failed)
    print('%d knots settled exactly, %d upper bounds lowered' % (len(settled), lowered))
    if '--selftest' in sys.argv:
        import copy, random
        random.seed(0)
        sample = [c for c in certs if c['target'] != 'unknot'][:20]
        tests = {
            'other smoothing': lambda c: c.update(smoothing=1 - c['smoothing']),
            'other crossing': lambda c: c.update(crossing=(c['crossing'] + 1) % len(c['diagram'])),
            'wrong target': lambda c: c.update(target='12a_1'),
            'bound too small': lambda c: c.update(bound=c['bound'] - 1),
        }
        for name, f in tests.items():
            rejected = timed = 0
            for c in sample:
                d = copy.deepcopy(c)
                f(d)
                try:
                    why = check_limited(d, rows, settled, 60)
                except Exception as e:
                    why = 'error: %s' % e
                rejected += why is not None
                timed += why is not None and why.startswith('time limit')
            print('selftest %-16s rejected %d of %d (%d by the time limit)' % (name, rejected, len(sample), timed))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
