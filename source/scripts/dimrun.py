import pickle
import proc
from ext import *
f=Film(); sl=slots()
bl=np.median(cv2.GaussianBlur(f.frame(sl[20]),(0,0),3).reshape(-1,3),axis=0)
print('black level',bl)
gapp={}
def norm_dim(im):
    b=cv2.GaussianBlur(im,(0,0),2.6)
    r=(b-bl)/np.maximum(plate-bl,1)
    g=np.median(r.reshape(-1,3)[::23],axis=0); g=np.maximum(g,1e-3)
    rn=r/g
    ink0=((1-rn.min(2))>0.25)|(~validb)
    ink0=cv2.dilate(ink0.astype(np.uint8),np.ones((9,9),np.uint8))>0
    wgt=(~ink0).astype(np.float32)
    den=cv2.GaussianBlur(wgt,(0,0),40); num=cv2.GaussianBlur(rn*wgt[...,None],(0,0),40)
    field=np.where(den[...,None]>0.04,num/np.maximum(den[...,None],1e-4),1.0)
    pmv=plate[validb].mean(0)
    return rn/field,(bl+g*(pmv-bl))/pmv
proc.normalize=norm_dim
out={}
for k in range(0,71):
    im=f.frame(sl[k])
    if k<38: out[k]=([],np.array([0.16,0.15,0.13],np.float32),sl[k]); continue
    g0=np.median((cv2.GaussianBlur(im,(0,0),1.2)/np.maximum(plate,1)).reshape(-1,3)[::23],axis=0)
    if g0.max()>=0.6: continue
    polys,g=proc.process(im,2.0)
    polys=[(c.astype(np.float32),[r.astype(np.int16) for r in rings]) for c,rings,ar in polys if ar>=150]
    # mark as "bright enough" for the cleaner by passing a pseudo gain; real gain kept separately
    out[k]=(polys,g.astype(np.float32),sl[k]); print(k,len(polys),g.round(2))
pickle.dump(out,open(S+'/dimraw_0000.pkl','wb'))
