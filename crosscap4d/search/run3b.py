import sys, json, os, time
sys.argv=[sys.argv[0]]+sys.argv[1:]
import run3, probe
prev=[json.loads(l) for f in sys.argv[3:] for l in open(f)]
NEW={r['knot']:r['bound'] for r in prev if not r.get('failed')}
orig=probe.gam
probe.gam=lambda n: orig(n) if orig(n) is not None else NEW.get(n)
if __name__=='__main__':
    from multiprocessing import Pool
    ndiag=int(sys.argv[1]); out=sys.argv[2]
    so=json.load(open('../data/still_open.json'))
    done=set(NEW)
    if os.path.exists(out): done|={json.loads(l)['knot'] for l in open(out)}
    todo=[(x['knot'],*x['knotinfo_range'],ndiag) for x in so if x['knot'] not in done]
    t=time.time(); n=c=0
    with Pool(4) as P, open(out,'a') as f:
        for r in P.imap_unordered(run3.work,todo,chunksize=1):
            if not r.get('failed') and r['target'] in NEW: r['target_from_this_file']=True
            f.write(json.dumps(r)+'\n'); f.flush(); n+=1; c+=not r.get('failed')
            if n%100==0: print(n,c,round(time.time()-t),flush=True)
    print('DONE',n,c,round(time.time()-t),flush=True)
