import glob, pickle, sys, time
from multiprocessing import Pool
K=28
def load_raw():
    import pickle,glob
    from common import S
    raw={}
    for p in glob.glob(S+'/raw_*.pkl'): raw.update(pickle.load(open(p,'rb')))
    return raw
def make_palette(raw):
    from common import S,np,cv2
    cols=[];wts=[]
    for k,(polys,g,vf) in raw.items():
        if g.max()<0.25: continue
        for col,rings in polys:
            a=cv2.contourArea(rings[0].astype(np.int32))
            if a<40: continue
            cols.append(np.clip(col,0,1.41)); wts.append(a)
    cols=np.array(cols,np.float32); wts=np.array(wts)
    # sample proportional to sqrt(area) so that rare bright colours survive
    p=np.sqrt(wts); p/=p.sum(); rng=np.random.default_rng(0)
    samp=cols[rng.choice(len(cols),min(150000,len(cols)*2),p=p)]
    crit=(cv2.TERM_CRITERIA_EPS+cv2.TERM_CRITERIA_MAX_ITER,80,1e-4)
    _,_,cen=cv2.kmeans(samp,K,None,crit,5,cv2.KMEANS_PP_CENTERS)
    return cen
def clean(polys,g,cen,eps):
    from common import np,cv2,W,H
    dim=g.max()<0.6
    if g.max()<0.25 or not polys: return []
    I=np.full((H,W),-1,np.int16)
    for col,rings in polys:
        if dim and cv2.contourArea(rings[0].astype(np.int32))<120: continue
        idx=int(((cen-np.clip(col,0,1.41))**2).sum(1).argmin())
        cv2.fillPoly(I,[r.astype(np.int32) for r in rings],idx)
    ink=I>=0
    if ink.sum()<45: return []
    if dim:
        inkm=cv2.morphologyEx(ink.astype(np.uint8),cv2.MORPH_OPEN,np.ones((5,5),np.uint8))>0
        n0,cl0,st0,_=cv2.connectedComponentsWithStats(inkm.astype(np.uint8),connectivity=8)
        big=st0[:,cv2.CC_STAT_AREA]>=1800; big[0]=False; inkm=big[cl0]
        I[~inkm]=-1; ink=inkm
        if ink.sum()<45: return []
    present=[c for c in np.unique(I) if c>=0]
    best=np.full((H,W),-1.0,np.float32); Ls=np.full((H,W),-1,np.int16)
    sig=2.6 if dim else 1.4
    for c in present:
        m=cv2.GaussianBlur((I==c).astype(np.float32),(0,0),sig)
        up=m>best; best[up]=m[up]; Ls[up]=c
    Ls[~ink]=-1
    # small fragments -> unknown, then filled from nearest known neighbour (if one is close)
    unk=np.zeros((H,W),bool)
    amin=260 if dim else 70
    for c in present:
        n,cl,st,_=cv2.connectedComponentsWithStats((Ls==c).astype(np.uint8),connectivity=4)
        if n<=1: continue
        small=st[:,cv2.CC_STAT_AREA]<amin; small[0]=False
        if small.any(): unk|=small[cl]
    if unk.any():
        known=(Ls>=0)&~unk
        if known.any():
            dist,lab=cv2.distanceTransformWithLabels((~known).astype(np.uint8),cv2.DIST_L2,3,labelType=cv2.DIST_LABEL_PIXEL)
            ys,xs=np.nonzero(known); lut=np.zeros(lab.max()+1,np.int16); lut[lab[ys,xs]]=Ls[ys,xs]
            near=unk&(dist<=2.5)
            # a fragment is embedded if any of its pixels touches known ink; spread decision over component
            n,cl=cv2.connectedComponents(unk.astype(np.uint8),connectivity=8)
            touch=np.zeros(n,bool); touch[np.unique(cl[near])]=True; touch[0]=False
            emb=touch[cl]
            Ls[emb]=lut[lab[emb]]
    out=[]
    for c in np.unique(Ls[Ls>=0]):
        m=(Ls==c).astype(np.uint8)
        cs,hier=cv2.findContours(m,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_NONE)
        if hier is None: continue
        hier=hier[0]
        for i,cnt in enumerate(cs):
            if hier[i][3]!=-1: continue
            area=cv2.contourArea(cnt)
            if area<(120 if dim else 30): continue
            rings=[cv2.approxPolyDP(cnt,eps,True)[:,0,:]]
            if len(rings[0])<3: continue
            j=hier[i][2]
            while j!=-1:
                if cv2.contourArea(cs[j])>=40:
                    rr=cv2.approxPolyDP(cs[j],eps,True)[:,0,:]
                    if len(rr)>=3: rings.append(rr)
                j=hier[j][0]
            out.append((int(c),[r.astype(np.int16) for r in rings],float(area)))
    out.sort(key=lambda p:-p[2])
    return [(c,r) for c,r,a in out]
def work(args):
    path,eps=args
    import pickle
    from common import S,np
    raw=pickle.load(open(path,'rb')); cen=np.load(S+'/pal.npy'); out={}
    for k,(polys,g,vf) in raw.items(): out[k]=(clean(polys,g,cen,eps),g)
    return out
if __name__=='__main__':
    import os
    from common import S,np
    eps=float(sys.argv[1]) if len(sys.argv)>1 else 2.0
    t=time.time()
    if not os.path.exists(S+'/pal.npy') or '--pal' in sys.argv:
        raw=load_raw(); cen=make_palette(raw); np.save(S+'/pal.npy',cen); del raw
    cen=np.load(S+'/pal.npy'); print('palette',round(time.time()-t),flush=True)
    files=sorted(glob.glob(S+'/raw_*.pkl'))+sorted(glob.glob(S+'/dimraw_*.pkl'))
    res={}
    with Pool(int(sys.argv[2]) if len(sys.argv)>2 else 6) as p:
        for r in p.imap(work,[(f,eps) for f in files]): res.update(r)
    pickle.dump((res,cen),open(S+'/clean.pkl','wb'))
    pts=sum(len(r) for k in res for c,rr in res[k][0] for r in rr); pol=sum(len(res[k][0]) for k in res)
    print('frames',len(res),'nonempty',sum(1 for k in res if res[k][0]),'polys',pol,'pts',pts,'time',round(time.time()-t))
