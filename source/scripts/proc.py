from ext import *
cen=np.load(S+'/km_cen.npy')
EPS=1.5
def process(im,eps=EPS):
    R,g=normalize(im); ink,d=inkmask(R)
    polys=[]
    if ink.sum()<45: return polys,g
    C=corecolor(R,ink)
    ys,xs=np.nonzero(ink)
    f=C[ys,xs]
    lab=((f[:,None,:]-cen[None])**2).sum(2).argmin(1)
    L=np.full((H,W),-1,np.int32); L[ys,xs]=lab
    present=np.unique(lab)
    best=np.full((H,W),-1.0,np.float32); Ls=np.full((H,W),-1,np.int32)
    for c in present:
        m=cv2.GaussianBlur((L==c).astype(np.float32),(0,0),2.0)
        up=m>best; best[up]=m[up]; Ls[up]=c
    Ls[~ink]=-1
    # reassign small embedded fragments to neighbouring class
    k3=np.ones((5,5),np.uint8)
    for c in np.unique(Ls[Ls>=0]):
        n,cl,st,_=cv2.connectedComponentsWithStats((Ls==c).astype(np.uint8),connectivity=8)
        for i in range(1,n):
            ar=st[i,cv2.CC_STAT_AREA]
            if ar>=90: continue
            x,y,w,h=st[i,:4]; x0=max(x-3,0); y0=max(y-3,0); x1=min(x+w+3,W); y1=min(y+h+3,H)
            sub=(cl[y0:y1,x0:x1]==i).astype(np.uint8)
            ring=(cv2.dilate(sub,k3)>0)&(sub==0)
            nb=Ls[y0:y1,x0:x1][ring]
            inkfrac=(nb>=0).mean() if nb.size else 0
            if inkfrac>0.45:
                vals,cn=np.unique(nb[nb>=0],return_counts=True)
                Ls[y0:y1,x0:x1][sub>0]=vals[cn.argmax()]
    for c in np.unique(Ls[Ls>=0]):
        m=(Ls==c).astype(np.uint8)
        cs,hier=cv2.findContours(m,cv2.RETR_CCOMP,cv2.CHAIN_APPROX_NONE)
        if hier is None: continue
        hier=hier[0]
        for i,cnt in enumerate(cs):
            if hier[i][3]!=-1: continue
            area=cv2.contourArea(cnt)
            if area<16: continue
            rings=[cv2.approxPolyDP(cnt,eps,True)[:,0,:]]
            j=hier[i][2]
            while j!=-1:
                if cv2.contourArea(cs[j])>=24:
                    rr=cv2.approxPolyDP(cs[j],eps,True)[:,0,:]
                    if len(rr)>=3: rings.append(rr)
                j=hier[j][0]
            if len(rings[0])<3: continue
            x,y,w,h=cv2.boundingRect(cnt)
            mm=np.zeros((h,w),np.uint8); cv2.drawContours(mm,cs,i,255,-1,offset=(-x,-y))
            sel=(mm>0)&(Ls[y:y+h,x:x+w]==c)
            if not sel.any(): continue
            col=np.median(C[y:y+h,x:x+w][sel],axis=0)
            polys.append((col,rings,area))
    polys.sort(key=lambda p:-p[2])
    return polys,g
def render(polys,g,scale=0.5):
    bg=np.clip(plate*g,0,255)
    out=bg.copy()
    pc=bg.reshape(-1,3).mean(0)
    for col,rings,area in polys:
        c=np.clip(col*pc,0,255).tolist()
        cv2.fillPoly(out,[r.astype(np.int32) for r in rings],c,lineType=cv2.LINE_AA)
        cv2.polylines(out,[rings[0].astype(np.int32)],True,c,1,cv2.LINE_AA)
    return cv2.resize(out.astype(np.uint8),None,fx=scale,fy=scale,interpolation=cv2.INTER_AREA)
if __name__=='__main__':
    f=Film(); sl=slots(); tiles=[]
    ks=[int(float(a)*12) for a in sys.argv[1:]] or [72,216,312,648,1056,1152,1566,1632,1176,620,740,1620]
    for k in ks:
        im=f.frame(sl[k]); polys,g=process(im)
        npts=sum(len(r) for p in polys for r in p[1])
        row=np.hstack([cv2.resize(im.astype(np.uint8),None,fx=0.5,fy=0.5),render(polys,g)])
        cv2.putText(row,f'k{k} t{k/12:.1f} polys {len(polys)} pts {npts}',(8,24),cv2.FONT_HERSHEY_SIMPLEX,0.6,(0,255,255),2)
        tiles.append(row)
    for a in range(0,len(tiles),3):
        cv2.imwrite(S+f'/frames/proc_{a//3}.jpg',np.vstack(tiles[a:a+3]),[cv2.IMWRITE_JPEG_QUALITY,90])
