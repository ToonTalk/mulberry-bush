import sys, pickle, time
from multiprocessing import Pool
def work(args):
    a,b=args
    from proc import process, Film, slots, S
    import numpy as np
    f=Film(); sl=slots(); out={}
    for k in range(a,min(b,len(sl))):
        im=f.frame(sl[k])
        if im is None: continue
        polys,g=process(im)
        out[k]=([(c.astype(np.float32),[r.astype(np.int16) for r in rings]) for c,rings,ar in polys],g.astype(np.float32),sl[k])
    pickle.dump(out,open(f'{S}/raw_{a:04d}.pkl','wb'))
    return a,len(out)
if __name__=='__main__':
    t=time.time(); N=2095; step=60
    jobs=[(a,a+step) for a in range(0,N,step)]
    with Pool(7) as p:
        for r in p.imap_unordered(work,jobs): print(r,round(time.time()-t),flush=True)
    print('done',round(time.time()-t))
