"""Lower bounds for gamma_4 of alternating knots from Donaldson's diagonalisation theorem.

Theorems 2.10, 2.11 and 2.12 of Jabuka and Kelly (Algebr. Geom. Topol. 18 (2018)), applied to the
two definite Goeritz forms G_+ (positive) and G_- (negative) of an alternating diagram, with
sigma = sigma(K) and the residue s = sigma + 4 Arf(K) mod 8:

  s = 2:  if -G_- (+) [l] embeds in Z^{r+1} for no admissible l, then gamma_4 >= 2;
  s = 6:  the same with G_+;
  s = 0:  if neither G_+ (+) [l] nor -G_- (+) [l] embeds, for any admissible l, then gamma_4 >= 2;
  s = 4:  if G_+ does not embed in Z^{rank+2} and -G_- does not embed in Z^{rank+2},
          then gamma_4 >= 3.

Here r is the rank of the form and l is admissible when l divides det K with det K / l a square.
An embedding of P (+) [l] into Z^{r+1} is an embedding of P whose orthogonal complement, generated
by a primitive vector w, contains a vector of norm l, so l = k^2 |w|^2.
"""
import os, sys
from math import isqrt
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'verify'))
import goeritz as g, embed as E

BUDGET = 20_000_000


def admissible(l, det):
    return det % l == 0 and isqrt(det // l) ** 2 == det // l


def complement_norms(P, budget):
    N = len(P) + 1
    return sorted({E.complement_norm(v, N) for v in E.embeddings(P, N, budget=budget)})


def blocked(P, det, budget):
    """(True if P (+) [l] embeds in Z^{r+1} for no admissible l, complement norms found)"""
    w2s = complement_norms(P, budget)
    for w2 in w2s:
        k = 1
        while k * k * w2 <= det:
            if admissible(k * k * w2, det):
                return False, w2s
            k += 1
    return True, w2s


def embeds(P, N, budget):
    for _ in E.embeddings(P, N, budget=budget):
        return True
    return False


def forms(pd):
    """sigma, G_+ and -G_- (both positive definite, as lists) of an alternating diagram."""
    o = g.both(pd)
    if o[0][2] != o[1][2]:
        raise ValueError('the two colourings give different signatures')
    Gp = Gm = None
    for G, mu, s in o:
        ev = np.linalg.eigvalsh(G.astype(float)) if G.size else np.array([])
        if (ev > 0).all():
            Gp = [[int(x) for x in r] for r in G]
        elif (ev < 0).all():
            Gm = [[-int(x) for x in r] for r in G]
    if Gp is None or Gm is None:
        raise ValueError('diagram is not alternating: a Goeritz form is indefinite')
    return o[0][2], Gp, Gm


def analyse(pd, arf, det, budget=BUDGET):
    sigma, Pp, Pm = forms(pd)
    s8 = (sigma + 4 * arf) % 8
    res = {'sigma': sigma, 'class': s8, 'rank_plus': len(Pp), 'rank_minus': len(Pm)}
    if s8 in (2, 6):
        b, w = blocked(Pm if s8 == 2 else Pp, det, budget)
        res.update(theorem='2.10', bound=2 if b else None, complement_norms=w)
    elif s8 == 0:
        b1, w1 = blocked(Pp, det, budget)
        b2, w2 = blocked(Pm, det, budget) if b1 else (False, [])
        res.update(theorem='2.12', bound=2 if (b1 and b2) else None,
                   complement_norms=[w1, w2])
    else:
        e1 = embeds(Pp, len(Pp) + 2, budget)
        e2 = embeds(Pm, len(Pm) + 2, budget) if not e1 else True
        res.update(theorem='2.11', bound=3 if not (e1 or e2) else 2)
    return res
