import numpy as np, itertools
IRRED={4:(2,[1,1]),8:(2,[1,1,0]),9:(3,[2,0]),16:(2,[1,1,0,0]),25:(5,[2,0]),27:(3,[1,1,0]),49:(7,[3,0])}
# element = coefficient vector c0..c_{k-1}; modulus x^k = sum r_i x^i  (list r gives r_0..r_{k-1})
def make(q):
    if q not in IRRED:
        p=q; k=1; red=None
    else:
        p,red=IRRED[q]; k=len(red)
    els=list(itertools.product(range(p),repeat=k))
    ix={e:i for i,e in enumerate(els)}
    def mulp(a,b):
        prod=[0]*(2*k-1)
        for i in range(k):
            for j in range(k): prod[i+j]+=a[i]*b[j]
        for d in range(2*k-2,k-1,-1):
            c=prod[d]; prod[d]=0
            for i in range(k): prod[d-k+i]+=c*red[i]
        return tuple(x%p for x in prod[:k])
    A=np.array([[ix[tuple((x+y)%p for x,y in zip(a,b))] for b in els] for a in els],np.int32)
    M=np.array([[ix[mulp(a,b)] if k>1 else ix[((a[0]*b[0])%p,)] for b in els] for a in els],np.int32)
    N=np.array([ix[tuple((-x)%p for x in a)] for a in els],np.int32)
    # check field: every nonzero has inverse
    zero=ix[tuple([0]*k)]; one=ix[tuple([1]+[0]*(k-1))]
    for a in range(q):
        if a!=zero: assert (M[a]==one).any(), 'not a field'
    return A,M,N,zero,one,els
