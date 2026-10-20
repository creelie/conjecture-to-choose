import spherogram
from spherogram import Crossing, Link
def link_from_pd_unoriented(pd):
    """pd: list of 4-tuples; strand x0-x2 under, x1-x3 over. Returns Link or None, plus count of free loops."""
    if not pd: return None
    cs=[Crossing(i) for i in range(len(pd))]
    where={}
    for i,t in enumerate(pd):
        for j,l in enumerate(t): where.setdefault(l,[]).append((i,j))
    for l,ends in where.items():
        assert len(ends)==2,(l,ends)
        (i,j),(k,m)=ends
        cs[i][j]=cs[k][m]
    return Link(cs)
def smooth(pd,idx,kind):
    """remove crossing idx joining (a,b),(c,d) if kind==0 else (a,d),(b,c). returns new pd, number of free circles"""
    a,b,c,d=pd[idx]
    rest=[list(t) for k,t in enumerate(pd) if k!=idx]
    pairs=[(a,b),(c,d)] if kind==0 else [(a,d),(b,c)]
    loops=0
    for x,y in pairs:
        if x==y: loops+=1; continue
        for t in rest:
            for q in range(4):
                if t[q]==y: t[q]=x
        # also update the other pair labels
        pairs=[(p if p!=y else x, r if r!=y else x) for p,r in pairs]
    # labels x appearing once? fine since merged
    return [tuple(t) for t in rest], loops
