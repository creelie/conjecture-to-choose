Papers, certificates and verifiers for two partial results on the KnotInfo tables (version 2026.10.5), by Deep Bhattacharjee. Neither has been refereed.

**Nonorientable four-genus** (`crosscap4d/`). KnotInfo leaves the smooth nonorientable four-genus γ₄ open for 3,525 prime knots with 11 to 13 crossings. One pinch move, to a slice knot or to a knot whose γ₄ is known, settles 2,093 of them (465 at γ₄ = 1, 1,628 at γ₄ = 2) and lowers the upper bound of 575 more; 1,432 stay open. New in this release: 139 knots settled, after the verifier gained a complement test from forty seeded simplifications in Regina. Check with `pip install regina database_knotinfo` and `python3 crosscap4d/verify/verify.py`.

**Bridge index** (`paper/`, `data/`, `verify/`). For 243 of the 536 thirteen-crossing knots with bridge index [3,4] the bridge index is 4 and equals the meridional rank. The other 293 stay open. New in this release: Alexander-quandle colourings modulo every prime below 110, and closed 3-braids in a bounded range of Murasugi normal forms, settle none of them. Check with `python3 verify/verify.py`.

| group | image of a meridian | knots |
|---|---|---|
| Sp(4, F₃) | transvection | 67 |
| Sp(4, F₅) | transvection | 161 |
| O(4, F₅) | reflection | 15 |

Attached: both papers (`bridge13.pdf`, `crosscap4d.pdf`) and the whole repository as a zip.
