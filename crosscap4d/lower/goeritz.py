"""Goeritz matrices and the Gordon-Litherland signature of a knot diagram.

The PD code is KnotInfo's: each crossing (a,b,c,d) lists its edges counterclockwise, starting
with the incoming under-strand a, so the under-strand runs a -> c, and the edge labels increase
along the orientation. Corners: corner i of a crossing is the region between its edges i and
i+1. For a checkerboard colouring with shaded colour s, a crossing has weight eta = +1 when the
shaded regions are the corners 1 and 3 (between b,c and d,a) and -1 otherwise; the Goeritz
matrix is indexed by the unshaded regions with one region deleted, g_ij = -sum eta over the
crossings meeting regions i and j, and g_ii = -sum_{k != i} g_ik. A crossing is of type II for
the shaded surface when the region between its two incoming strands is shaded, and
mu = sum of eta over type II crossings. Then sigma(K) = sign(G) - mu (Gordon-Litherland).
A global change of the sign of eta replaces every quantity by that of the mirror image, so the
lower bounds, which are mirror invariant, do not depend on it; the verifier checks that both
colourings give the same signature and that |sigma| agrees with KnotInfo.
"""
import numpy as np

def faces(pd):
    pos = {}
    for X, t in enumerate(pd):
        for i, l in enumerate(t):
            pos.setdefault(l, []).append((X, i))
    seen = {}
    F = []
    for X in range(len(pd)):
        for i in range(4):
            if (X, i) in seen:
                continue
            f = []
            c = (X, i)
            while c not in seen:
                seen[c] = len(F); f.append(c)
                Xc, ic = c
                e = pd[Xc][(ic + 1) % 4]
                o = [p for p in pos[e] if p != (Xc, (ic + 1) % 4)]
                c = o[0] if o else (Xc, (ic + 1) % 4)
            F.append(f)
    return F, seen

def colour(pd):
    F, cf = faces(pd)
    assert len(F) == len(pd) + 2, (len(F), len(pd))
    col = {0: 0}; stack = [0]
    adj = {k: set() for k in range(len(F))}
    for X in range(len(pd)):
        for i in range(4):
            a, b = cf[(X, i)], cf[(X, (i + 1) % 4)]
            adj[a].add(b); adj[b].add(a)
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if v not in col:
                col[v] = 1 - col[u]; stack.append(v)
            else:
                assert col[v] != col[u]
    return F, cf, col

def gl(pd, shade, typerule='A'):
    """Goeritz matrix of the surface on faces of colour `shade`, and mu. Returns (G, mu)."""
    n2 = 2 * len(pd)
    F, cf, col = colour(pd)
    white = [k for k in range(len(F)) if col[k] != shade]
    idx = {k: j for j, k in enumerate(white)}
    m = len(white)
    G = np.zeros((m, m), dtype=np.int64)
    mu = 0
    for X, (a, b, c, d) in enumerate(pd):
        r = [cf[(X, i)] for i in range(4)]
        sh13 = col[r[1]] == shade   # shaded = {R_bc, R_da}
        eta = 1 if sh13 else -1
        w = [r[0], r[2]] if sh13 else [r[1], r[3]]
        i, j = idx[w[0]], idx[w[1]]
        if i != j:
            G[i, j] -= eta; G[j, i] -= eta
            G[i, i] += eta; G[j, j] += eta
        over_bd = (d - b) % n2 == 1
        inin = 0 if over_bd else 3
        has_inin = (col[r[inin]] == shade)
        type2 = has_inin if typerule == 'A' else not has_inin
        if type2:
            mu += eta
    k = int(np.argmax(np.abs(np.diag(G))))
    keep = [i for i in range(m) if i != k]
    return G[np.ix_(keep, keep)], mu

def sig(G):
    if G.size == 0:
        return 0
    ev = np.linalg.eigvalsh(G.astype(float))
    return int((ev > 1e-9).sum() - (ev < -1e-9).sum())

def both(pd, typerule='A'):
    out = []
    for s in (0, 1):
        G, mu = gl(pd, s, typerule)
        out.append((G, mu, sig(G) - mu))
    return out
