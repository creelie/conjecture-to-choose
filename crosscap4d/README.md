# Nonorientable four-genus of knots with 11 to 13 crossings

The smooth nonorientable four-genus γ₄(K) of a knot is the least first Betti number of a
smooth nonorientable surface in B⁴ bounded by K (γ₄ = 1 for slice knots). KnotInfo
(version 2026.10.5) gives only an interval for γ₄ of 3,525 prime knots with 11 to 13
crossings.

**Result (partial).**

- 2,537 of these knots now have a known γ₄: 520 have γ₄ = 1, 1,995 have γ₄ = 2 and 22 have
  γ₄ = 3.
- For 376 more knots the interval is narrower.
- The value stays open for 988 knots, including those 376.

The paper is [`paper/crosscap4d.pdf`](paper/crosscap4d.pdf). The pinch certificates are in
[`data/certificates.json`](data/certificates.json), the lower bounds in
[`data/lower_bounds.json`](data/lower_bounds.json) and the open knots, with their current
intervals, in [`data/still_open.json`](data/still_open.json).

| crossings | open in KnotInfo | settled at γ₄ = 1 | settled at γ₄ = 2 | settled at γ₄ = 3 | interval narrowed | unchanged |
|---|---|---|---|---|---|---|
| 11 | 59 | 0 | 49 | 0 | 1 | 9 |
| 12 | 455 | 45 | 308 | 7 | 35 | 60 |
| 13 | 3,011 | 475 | 1,638 | 15 | 340 | 543 |
| all | 3,525 | 520 | 1,995 | 22 | 376 | 612 |

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

The slice status and the γ₄ values of the targets are read from KnotInfo. In two
certificates the target is a knot settled earlier in the same file.

## The lower bounds

For an alternating knot both Goeritz forms of its alternating diagram are definite, and
Jabuka and Kelly (Algebr. Geom. Topol. 18 (2018), Theorems 2.10 to 2.12) turn Donaldson's
diagonalisation theorem into a lower bound. If K bounded a Möbius band (or, when
σ + 4 Arf ≡ 4 mod 8, a surface with b₁ = 2), gluing its double branched cover to the
double cover bounded by a checkerboard surface would give a closed definite four-manifold,
so a Goeritz lattice, plus a rank-one lattice [ℓ] with ℓ | det K and det K/ℓ a square, would
embed in the standard lattice of the same rank. The programs in [`lower/`](lower/) compute
both Goeritz forms and the signature (Gordon–Litherland) from the KnotInfo diagram, and
list every embedding of the lattice into ℤʳ⁺¹ (or ℤʳ⁺²) up to signed permutations of the
coordinates. When none exists with an admissible ℓ, γ₄ ≥ 2 (or ≥ 3). This raises the
KnotInfo lower end for 382 of the open knots: 360 to γ₄ ≥ 2 and 22 to γ₄ ≥ 3.

None of the 520 Möbius bands appears in the Lee–Sabloff data
(github.com/LeeJoPing/Mobius-Band-Search), their data list no Möbius band for any of the 382
knots whose lower bound is raised here, and no settled value contradicts their
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
gets four seeded attempts and two minutes. All 2,728 certificates in the file pass. A candidate that the
check does not accept is not in the file, and its knot is counted as open.

For the lower bounds (numpy and sympy):

```
python3 lower/verify_lower.py --selftest --certificates
```

It recomputes all 382 lower bounds with a shuffled search order, checks that both
checkerboard colourings give the same signature and that |σ| agrees with KnotInfo, and runs
two tests of the conventions:

- On the 511 alternating knots with at most eleven crossings whose γ₄ KnotInfo records, the
  bound never exceeds the recorded value. With the sign of σ reversed, it contradicts the
  recorded value for 216 of them.
- On the alternating knots of the certificate file, the bound never exceeds the bound the
  pinch certificate proves.

## Layout

- `data/certificates.json`: one record per knot. It holds the knot, the KnotInfo interval,
  the PD code of the diagram used, the crossing index, the smoothing (0: join (a,b),(c,d);
  1: join (a,d),(b,c) in the PD tuple (a,b,c,d)), the target, the bound, and whether the
  value is now settled.
- `data/lower_bounds.json`: the knots whose lower bound the Donaldson obstruction raises, with
  the theorem used, σ, the ranks of the Goeritz forms and the complement norms found.
- `data/still_open.json`: the knots that stay open, with their current interval, any verified
  upper bound and lower bound and, where a search candidate failed verification, that
  candidate.
- `lower/`: Goeritz forms and signature (`goeritz.py`), the embedding search (`embed.py`),
  the obstruction (`obstruct.py`), the run over the open knots (`run_lower.py`) and its
  verifier (`verify_lower.py`).
- `verify/verify.py`: the verifier (Regina and KnotInfo only).
- `search/`: the SnapPy search (`runall.py` first pass, `pass2.py` second pass with chained
  targets, `run3.py` and `run3b.py` third pass on six diagrams and fourth pass on twenty,
  with the seeded complement test of `certify.py`, `probe.py` pinch moves and
  identification, `merge4.py` the merge of the fourth pass and the lower bounds).
- `paper/`: the paper; `make_tables.py` writes `generated.tex` from the data.
