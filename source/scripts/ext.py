from common import *
plate=get_plate()
valid=np.zeros((H,W),np.uint8)
def rrect(img,x0,y0,x1,y1,r,val):
    cv2.rectangle(img,(x0+r,y0),(x1-r,y1),val,-1); cv2.rectangle(img,(x0,y0+r),(x1,y1-r),val,-1)
    for cx,cy in ((x0+r,y0+r),(x1-r,y0+r),(x0+r,y1-r),(x1-r,y1-r)): cv2.circle(img,(cx,cy),r,val,-1)
rrect(valid,10,10,W-11,H-11,36,255)
validb=valid>0
def normalize(im):
    b=cv2.GaussianBlur(im,(0,0),1.2)
    r=b/np.maximum(plate,1)
    g=np.median(r.reshape(-1,3)[::23],axis=0); g=np.maximum(g,1e-3)
    rn=r/g
    ink0=((1-rn.min(2))>0.18)|(~validb)
    ink0=cv2.dilate(ink0.astype(np.uint8),np.ones((9,9),np.uint8))>0
    wgt=(~ink0).astype(np.float32)
    den=cv2.GaussianBlur(wgt,(0,0),40)
    num=cv2.GaussianBlur(rn*wgt[...,None],(0,0),40)
    field=np.where(den[...,None]>0.04,num/np.maximum(den[...,None],1e-4),1.0)
    return rn/field, g
def inkmask(R,weak_t=0.13,strong_t=0.3):
    d=1-R.min(2)
    weak=((d>weak_t)&validb).astype(np.uint8)
    n,lab,st,_=cv2.connectedComponentsWithStats(weak,connectivity=8)
    strong=(d>strong_t)&validb
    cnt=np.bincount(lab[strong],minlength=n)
    keep=(cnt>=12)&(st[:,cv2.CC_STAT_AREA]>=45); keep[0]=False
    return keep[lab], d
def corecolor(R,ink):
    a=np.clip(1-R,-0.4,1.0)
    w=ink.astype(np.float32)
    den=cv2.GaussianBlur(w,(0,0),1.5)+1e-4
    a_s=cv2.GaussianBlur(a*w[...,None],(0,0),1.5)/den[...,None]
    m_s=a_s.max(2)
    mag=a.max(2)
    dist=cv2.distanceTransform(ink.astype(np.uint8),cv2.DIST_L2,3)
    M=np.where(dist<3.5,cv2.dilate(mag,np.ones((7,7),np.uint8)),mag)
    scale=np.clip(M/np.maximum(m_s,0.05),0.5,3.0)
    return np.clip(1-a_s*scale[...,None],0,1.4).astype(np.float32)
def slots():
    d=np.load(S+'/diff.npy'); out=[]
    k=0
    while True:
        lo=int(np.ceil(2.5*k)); hi=int(np.ceil(2.5*(k+1)))
        if hi>5239: break
        js=list(range(lo,hi)); j=min(js,key=lambda j:d[j+1]); out.append(j); k+=1
    return out
