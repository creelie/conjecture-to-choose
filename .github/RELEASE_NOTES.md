Paper, certificates and verifiers for two partial results on the KnotInfo tables (version 2026.10.5), by Deep Bhattacharjee.

**New in this release: one paper.** *The bridge index and the nonorientable four-genus of knots with at most thirteen crossings* (`paper/paper1/knot-tables.pdf`, TeX source in `paper/paper2/knot-tables-tex.zip`) joins the two papers into one, Part I on the bridge index and Part II on the nonorientable four-genus. The results, certificates and verifiers are those of release 1.2.0; the totals are unchanged. It has not been refereed.

**Nonorientable four-genus** (`crosscap4d/`). KnotInfo leaves the smooth nonorientable four-genus γ₄ open for 3,525 prime knots with 11 to 13 crossings. Pinch moves give upper bounds and the Goeritz-lattice obstructions of Jabuka and Kelly (Donaldson's theorem) give lower bounds for the alternating knots; together they settle 2,537 of them (520 at γ₄ = 1, 1,995 at γ₄ = 2, 22 at γ₄ = 3) and narrow the interval of 376 more; 988 stay open. In release 1.2.0: 382 lower bounds raised by an exhaustive embedding search of the Goeritz lattices, and 84 pinch certificates from a search over twenty diagrams per knot, for 444 more knots settled. Check with `pip install regina database_knotinfo numpy sympy`, `python3 crosscap4d/verify/verify.py` and `python3 crosscap4d/lower/verify_lower.py --selftest --certificates`.

**Bridge index** (`paper/`, `data/`, `verify/`). For 243 of the 536 thirteen-crossing knots with bridge index [3,4] the bridge index is 4 and equals the meridional rank. The other 293 stay open. Alexander-quandle colourings modulo every prime below 110, and closed 3-braids in a bounded range of Murasugi normal forms, settle none of them. Check with `python3 verify/verify.py`.

| group | image of a meridian | knots |
|---|---|---|
| Sp(4, F₃) | transvection | 67 |
| Sp(4, F₅) | transvection | 161 |
| O(4, F₅) | reflection | 15 |

Attached: the joint paper (`knot-tables.pdf`), the two earlier papers (`bridge13.pdf`, `crosscap4d.pdf`) and the whole repository as a zip.
