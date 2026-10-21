"""Embeddings of a positive definite integral lattice (Gram matrix P) into the standard Z^N."""
import sys
from math import isqrt

def _sq_partitions(n, maxparts, maxval):
    """nonincreasing tuples of positive ints with sum of squares n"""
    if n == 0:
        yield (); return
    if maxparts == 0:
        return
    for a in range(min(maxval, isqrt(n)), 0, -1):
        for rest in _sq_partitions(n - a * a, maxparts - 1, a):
            yield (a,) + rest

def order_basis(P):
    r = len(P)
    order = [max(range(r), key=lambda i: P[i][i])]
    while len(order) < r:
        best = max((i for i in range(r) if i not in order),
                   key=lambda i: (sum(1 for j in order if P[i][j]), -P[i][i]))
        order.append(best)
    return order

def embeddings(P, N, limit=None, budget=5_000_000):
    """Yield lists of vectors (in original order) realising P in Z^N, up to signed
    permutations of coordinates. Raises RuntimeError when the node budget runs out."""
    r = len(P)
    order = order_basis(P)
    vecs = []          # vectors over touched coords, in `order`
    count = [0]
    def xs(i, t, n, k, partial, x):
        # coordinates 0..t-1 touched; choose x[k..]
        count[0] += 1
        if count[0] > budget:
            raise RuntimeError('budget')
        if k == t:
            for j in range(len(vecs)):
                if partial[j] != P[order[i]][order[j]]:
                    return
            yield list(x), n; return
        # bound: remaining coords can change partial[j] by at most sqrt(n)*||v_j rest||
        for j in range(len(vecs)):
            rem = sum(vecs[j][m] ** 2 for m in range(k, t))
            if (partial[j] - P[order[i]][order[j]]) ** 2 > n * rem:
                return
        a = isqrt(n)
        for v in range(-a, a + 1):
            for j in range(len(vecs)):
                partial[j] += v * vecs[j][k]
            x.append(v)
            yield from xs(i, t, n - v * v, k + 1, partial, x)
            x.pop()
            for j in range(len(vecs)):
                partial[j] -= v * vecs[j][k]
    def rec(i, t):
        if i == r:
            out = [None] * r
            for idx, o in enumerate(order):
                out[o] = vecs[idx] + [0] * (N - len(vecs[idx]))
            yield out; return
        n = P[order[i]][order[i]]
        for x, rem in list(xs(i, t, n, 0, [0] * len(vecs), [])):
            for y in _sq_partitions(rem, N - t, isqrt(rem)):
                newt = t + len(y)
                for v in vecs:
                    v.extend([0] * len(y))
                vecs.append(x + list(y))
                yield from rec(i + 1, newt)
                vecs.pop()
                for v in vecs:
                    del v[t:]
    yield from rec(0, 0)

def complement_norm(vecs, N):
    """norm of a primitive generator of the orthogonal complement (rank r = N-1)."""
    import sympy
    M = sympy.Matrix(vecs)
    ns = M.nullspace()
    assert len(ns) == 1
    w = ns[0]
    den = sympy.ilcm(*[e.q for e in w])
    w = [int(e * den) for e in w]
    from math import gcd
    g = 0
    for e in w:
        g = gcd(g, abs(e))
    w = [e // g for e in w]
    return sum(e * e for e in w)
