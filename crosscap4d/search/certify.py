"""Reproducible complement test: Regina complements of both diagrams, simplified under
fixed seeds, plus one level of retriangulation; any common isomorphism signature proves the
complements homeomorphic (hence the knots agree up to mirror image, Gordon-Luecke)."""
import regina
def _cloud(pd, n, height):
    sigs = set(); minsize = None; mins = []
    for k in range(n):
        regina.RandomEngine.reseedWithDefault()
        for _ in range(k * 7919):
            regina.RandomEngine.rand(1000)
        L = regina.Link.fromPD(pd)
        if k:
            L.simplify()
        T = L.complement(); T.simplify()
        sigs.add(T.isoSig())
        if minsize is None or T.size() < minsize:
            minsize = T.size(); mins = [T]
        elif T.size() == minsize:
            mins.append(T)
    if height:
        for T in mins[:6]:
            T.retriangulate(height, 1, lambda sig, tri: sigs.add(sig) or False)
    return sigs
_tcache = {}
def cloud_same(pd1, pd2, n=40, height=1):
    key = tuple(map(tuple, pd2))
    if key not in _tcache:
        _tcache[key] = _cloud(pd2, n, height)
    return bool(_cloud(pd1, n, height) & _tcache[key])
