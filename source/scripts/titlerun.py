import pickle
import ext, proc, repack
from ext import *
eps=float(sys.argv[1]) if len(sys.argv)>1 else 2.0
f=Film(); sl=slots(); cen=np.load(S+'/pal.npy'); N=len(sl)
pink=plate.copy(); pmp=pink[validb].mean(0)
def quickg(im): return np.median((cv2.GaussianBlur(im,(0,0),1.2)/np.maximum(pink,1)).reshape(-1,3)[::23],axis=0)
gs={k:quickg(f.frame(sl[k])) for k in range(1790,N)}
start=min(k for k in gs if gs[k][0]/gs[k][2]>1.2 and k>1800)
end=min(k for k in gs if k>start+60 and gs[k].max()<0.45)
print('violet from',start,start/12,'to',end,end/12)
f=Film()
acc=[cv2.GaussianBlur(f.frame(sl[k]),(0,0),2) for k in range(start+3,start+13)]
vio=cv2.GaussianBlur(np.median(np.array(acc),axis=0),(0,0),6).astype(np.float32)
cv2.imwrite(S+'/frames/violet_plate.png',vio.astype(np.uint8))
ext.plate=vio; proc.plate=vio
pmv=vio[validb].mean(0)
D={}; G={}; f=Film(); FR={}
for k in range(start,end):
    im=f.frame(sl[k]); FR[k]=im.astype(np.uint8) if k%1==0 else None
    R,g=ext.normalize(im); D[k]=np.clip(1-R.min(2),0,1).astype(np.float16); G[k]=(g*pmv/pmp).astype(np.float32)
ks=list(range(start,end))
s=np.array([np.clip(D[k].astype(np.float32)-0.14,0,1)[validb].mean() for k in ks]); ss=np.convolve(s,np.ones(5)/5,'same')
print('strength',' '.join(f'{v*1000:.0f}' for v in ss[::4]))
# cards: runs above threshold, split at deep dips
thr=0.10*ss.max(); cards=[]; i=0
while i<len(ks):
    if ss[i]>thr:
        j=i
        while j<len(ks) and ss[j]>thr: j+=1
        cards.append((i,j)); i=j
    else: i+=1
def split(a,b):
    seg=ss[a:b]
    if b-a<30: return [(a,b)]
    best=None
    for m in range(a+10,b-10):
        l=ss[a:m].max(); r=ss[m:b].max()
        if ss[m]<0.55*min(l,r) and (best is None or ss[m]<ss[best]): best=m
    return [(a,b)] if best is None else split(a,best)+split(best,b)
cards=[c for a,b in cards for c in split(a,b)]
print('cards',[(ks[a]/12,ks[b-1]/12) for a,b in cards])
out={}
for k in range(start,end): out[k]=('own',[],G[k])
for a,b in cards:
    m=a+int(np.argmax(ss[a:b])); km=ks[m]
    polys,g=proc.process(FR[km].astype(np.float32),eps)
    polys=[(c.astype(np.float32),[r.astype(np.int16) for r in rings]) for c,rings,ar in polys]
    cl=repack.clean(polys,np.ones(3,np.float32),cen,eps)
    lab=np.zeros((H,W),np.int32)
    for i,(c,rr) in reversed(list(enumerate(cl))): cv2.fillPoly(lab,[r.astype(np.int32) for r in rr],i+1)
    n=len(cl); cnt=np.bincount(lab.ravel(),minlength=n+1).astype(np.float32)+1e-3
    dm=np.bincount(lab.ravel(),weights=D[km].astype(np.float32).ravel(),minlength=n+1)/cnt
    cover=cv2.dilate((lab>0).astype(np.uint8),np.ones((9,9),np.uint8))>0
    out[km]=('own',cl,G[km]); miss=[]
    for i in range(a,b):
        k=ks[i]
        if k==km: continue
        dk=D[k].astype(np.float32)
        al=np.clip((np.bincount(lab.ravel(),weights=dk.ravel(),minlength=n+1)/cnt)[1:]/np.maximum(dm[1:],0.05),0,1)
        al[al<0.12]=0
        out[k]=('ref',km,np.round(al*255).astype(np.uint8),G[k])
        miss.append(float(((dk>0.3)&~cover&validb).sum()))
    print('card',km/12,'polys',n,'pts',sum(len(r) for c,rr in cl for r in rr),'max uncovered ink px',int(max(miss)) if miss else 0)
for k in range(end,N): out[k]=('own',[],gs[k].astype(np.float32))
pickle.dump((start,out),open(S+'/title.pkl','wb'))
