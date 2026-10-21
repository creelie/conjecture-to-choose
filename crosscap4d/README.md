# Nonorientable four-genus of knots with 11 to 13 crossings

The smooth nonorientable four-genus γ₄(K) of a knot is the least first Betti number of a
smooth nonorientable surface in B⁴ bounded by K (γ₄ = 1 for slice knots). KnotInfo
(version 2026.10.5) gives only an interval for γ₄ of 3,525 prime knots with 11 to 13
crossings.

**Result (partial).**

- 2,093 of these knots now have a known γ₄. For 465 of them γ₄ = 1, and for 1,628 of them
  γ₄ = 2.
- For 575 more knots the upper bound is lower.
- The value stays open for 1,432 knots, including those 575.

The paper is [`paper/crosscap4d.pdf`](paper/crosscap4d.pdf). The certificates are in
[`data/certificates.json`](data/certificates.json) and the open knots in
[`data/still_open.json`](data/still_open.json).

| crossings | open in KnotInfo | settled at γ₄ = 1 | settled at γ₄ = 2 | upper bound lowered | value still open |
|---|---|---|---|---|---|
| 11 | 59 | 0 | 33 | 9 | 26 |
| 12 | 455 | 41 | 254 | 69 | 160 |
| 13 | 3,011 | 424 | 1,341 | 497 | 1,246 |
| all | 3,525 | 465 | 1,628 | 575 | 1,432 |

## The proof

A **pinch move** smooths one crossing of a diagram in the way that does not respect the
orientation, so the result K′ is again a knot. The move is a nonorientable band move, so

- if K′ is slice, then K bounds a Möbius band in B⁴ and γ₄(K) ≤ 1;
- in general γ₄(K) ≤ γ₄(K′) + 1.

For every knot in the certificate file, one pinch move on a diagram of K gives one of two
things:

- a slice knot or the unknot. This settles γ₄ = 1, because a knot that is not slice has
  γ₄ ≥ 1.
- a knot with γ₄ = 1. This gives γ₄ ≤ 2. For the knots whose KnotInfo interval is [2,3] this
  settles γ₄ = 2. The lower bound 2 is the published obstruction recorded in KnotInfo from
  Lee and Sabloff (arXiv 2607.23582): the Arf invariant condition of Yasuhara or the
  linking form condition of Murakami and Yasuhara.

The slice status and the γ₄ values of the targets are read from KnotInfo. In three
certificates the target is a knot settled earlier in the same file.

None of the 465 Möbius bands appears in the Lee–Sabloff data
(github.com/LeeJoPing/Mobius-Band-Search), and no settled value contradicts their
obstructions.

## Checking it

```
pip install regina database_knotinfo
python3 verify/verify.py              # under an hour on 4 cores
python3 verify/verify.py --selftest   # also checks that corrupted certificates are rejected
```

The verifier does not use SnapPy, which the search used. For every certificate it checks
the following, using Regina:

- the stored diagram is a diagram of the knot;
- the named smoothing is non-orientable, so the result has one component;
- the result is the target knot up to mirror image, or the unknot.

Two diagrams are identified in one of two exact ways:

- a common diagram reached by Reidemeister moves;
- combinatorially isomorphic triangulations of the complements: either the simplified
  complements themselves, possibly after one Pachner move, or a triangulation that occurs
  among forty simplifications of each complement under fixed seeds of Regina's random engine
  (with the triangulations one Pachner move from the smallest of them). With Gordon–Luecke,
  this shows the knots are the same up to mirror image.

The unknot is recognised as the knot whose complement is a solid torus. Each certificate
gets four seeded attempts and two minutes. All 2,668 certificates in the file pass. A candidate that the
check does not accept is not in the file, and its knot is counted as open.

## Layout

- `data/certificates.json`: one record per knot. It holds the knot, the KnotInfo interval,
  the PD code of the diagram used, the crossing index, the smoothing (0: join (a,b),(c,d);
  1: join (a,d),(b,c) in the PD tuple (a,b,c,d)), the target, the bound, and whether the
  value is now settled.
- `data/still_open.json`: the knots that stay open, with any verified lower upper bound and,
  where a search candidate failed verification, that candidate.
- `verify/verify.py`: the verifier (Regina and KnotInfo only).
- `search/`: the SnapPy search (`runall.py` first pass, `pass2.py` second pass with chained
  targets, `run3.py` and `run3b.py` third pass on six diagrams with the seeded complement
  test of `certify.py`, `probe.py` pinch moves and identification).
- `paper/`: the paper; `make_tables.py` writes `generated.tex` from the data.
