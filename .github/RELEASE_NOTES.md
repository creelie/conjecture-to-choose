Paper, certificates and verifier for *Transvections and the bridge index of thirteen-crossing knots* by Deep Bhattacharjee.

KnotInfo (version 2026.10.5) lists the bridge index of 536 prime knots with 13 crossings as `[3,4]`. For 243 of them the bridge index is 4 and equals the meridional rank, so the meridional rank conjecture holds for these knots. The other 293 stay open. This is a partial result on a finite list and has not been refereed.

| group | image of a meridian | knots |
|---|---|---|
| Sp(4, F₃) | transvection | 67 |
| Sp(4, F₅) | transvection | 161 |
| O(4, F₅) | reflection | 15 |

Attached: the paper (`bridge13.pdf`) and the whole repository as a zip. Check the certificates with `python3 verify/verify.py` (standard library only), or with `pip install database_knotinfo==2026.10.5` and `python3 verify/verify.py --knotinfo` to also compare each PD code and each `[3,4]` entry with KnotInfo.
