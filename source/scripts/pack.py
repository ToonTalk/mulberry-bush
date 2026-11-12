import glob, pickle, gzip, base64, json, math
from ext import *
Q=int(sys.argv[1]) if len(sys.argv)>1 else 2
COLOR,SIL,STRIPE,DOT,BIG,POLKA,TITLE=1,2,4,8,16,32,64
cen=np.load(S+'/pal.npy'); K=len(cen); N=2095
clean={}; dimk={}
for p in sorted(glob.glob(S+'/clean_part_*.pkl')):
    for k,(polys,g,dimf) in pickle.load(open(p,'rb')).items():
        if dimf: dimk[k]=(polys,g)
        elif k not in dimk: clean[k]=(polys,g)
clean.update(dimk)
tstart,title=pickle.load(open(S+'/title.pkl','rb'))
beats=np.load(S+'/beats.npy'); d=np.load(S+'/diff.npy'); sl=slots()
# ---- plate / vignette
pm=plate[validb].mean(0); V=plate/pm; VS=float(np.percentile(V[validb],99.8))
small=cv2.resize((np.clip(V/VS,0,1)*255).astype(np.uint8),(256,188),interpolation=cv2.INTER_AREA)
ok,jb=cv2.imencode('.jpg',small,[cv2.IMWRITE_JPEG_QUALITY,88])
vig='data:image/jpeg;base64,'+base64.b64encode(jb.tobytes()).decode()
# ---- frames: ('own',polys,g) | ('ref',root,alpha|None,g)
fr=[]
for k in range(N):
    if k>=tstart: fr.append(title[k]); continue
    polys,g=clean.get(k,([],np.ones(3,np.float32)))
    if k>0 and fr[k-1][0] in('own','ref') and d[sl[k-1]+2:sl[k]+2].max()<1.5 and sl[k]>sl[k-1]:
        root=k-1 if fr[k-1][0]=='own' else fr[k-1][1]
        if k-root<250 and k not in dimk and root not in dimk: fr.append(('ref',root,None,g)); continue
    fr.append(('own',polys,g))
own=[f for f in fr if f[0]=='own']
print('own frames',len(own),'nonempty own',sum(1 for f in own if f[1]),'refs',N-len(own),'polys',sum(len(f[1]) for f in own),'pts',sum(len(r) for f in own for c,rr in f[1] for r in rr))
def geom(k):
    f=fr[k]; return fr[f[1]][1] if f[0]=='ref' else f[1]
# ---- media
def classify(polys):
    if not polys: return 0
    m=np.zeros((H//4+1,W//4+1),np.uint8); info=[]
    for c,rr in polys:
        col=cen[c]; o=rr[0].astype(np.int32); ar=cv2.contourArea(o); per=cv2.arcLength(o,True)+1e-3
        cv2.fillPoly(m,[o//4],255)
        (cx,cy),(w,h),_=cv2.minAreaRect(o); lo,hi=min(w,h)+1e-3,max(w,h)
        info.append((ar,4*math.pi*ar/per/per,hi/lo,lo,float(col.max()-col.min()),float(col.max()),o[:,0].mean()/4,o[:,1].mean()/4))
    m=cv2.dilate(m,np.ones((9,9),np.uint8)); n,lab=cv2.connectedComponents(m); flags=0
    for f in range(1,n):
        A=Ach=Abig=Agrey=Adark=0; nb=ns=nd=npoly=0; chbig=0
        for ar,circ,elong,lo,chroma,mx,cx,cy in info:
            if lab[min(int(cy),H//4),min(int(cx),W//4)]!=f: continue
            A+=ar; npoly+=1
            isbig=1500<=ar<=14000 and circ>0.6
            if isbig: nb+=1; Abig+=ar
            elif 50<=ar<=1000 and circ>0.55: nd+=1
            elif 40<=ar<=3500 and elong>=3 and lo<17: ns+=1
            if chroma>=0.22 and not isbig:
                Ach+=ar; chbig=max(chbig,ar)
            if chroma<0.2 and 0.35<=mx<0.8 and ar>2500: Agrey+=ar
            if mx<0.5 and ar>2500: Adark+=ar
        if A<1500: continue
        if nb>=2 and Abig>0.4*A: flags|=BIG
        elif Agrey>0.3*A and nd>=3: flags|=POLKA
        elif ns>=7 and ns>=0.4*npoly and Adark<0.35*A: flags|=STRIPE
        elif nd>=7 and nd>=0.4*npoly and Adark<0.35*A: flags|=DOT
        elif Ach>0.15*A and chbig>1500: flags|=COLOR
        elif Adark+Agrey>0.45*A: flags|=SIL
        elif ns>=5 and ns>=nd: flags|=STRIPE
        elif nd>=5: flags|=DOT
    return flags
fl=[classify(geom(k)) if k<tstart else 0 for k in range(N)]
mb=[]
for b in range(len(beats)):
    t0=beats[b]; t1=beats[b+1] if b+1<len(beats) else t0+0.5
    if t0*12>=tstart-2: mb.append(TITLE if t0<169.0 else 0); continue
    ks=[k for k in range(int(math.ceil(t0*12-0.5)),int(math.ceil(t1*12-0.5))) if 0<=k<N]
    f=0
    for bit in (COLOR,SIL,STRIPE,DOT,BIG,POLKA):
        if sum(1 for k in ks if fl[k]&bit)>=3: f|=bit
    mb.append(f)
try:
    exec(open(S+'/scripts/media_fix.py').read())
except FileNotFoundError: pass
names={COLOR:'c',SIL:'s',STRIPE:'=',DOT:'.',BIG:'O',POLKA:'p',TITLE:'T'}
for v in range(22):
    print(f'v{v:2d} {beats[v*16]:6.1f} '+' '.join(''.join(names[b] for b in names if x&b) or '-' for x in mb[v*16:v*16+16]))
# ---- encode
def varint(v,out):
    v=int(v)
    while True:
        b=v&127; v>>=7
        if v: out.append(b|128)
        else: out.append(b); break
def zz(v): return (v<<1)^(v>>31)
body=[]; table=bytearray()
for k,f in enumerate(fr):
    fb=bytearray(); ref=0
    if f[0]=='own':
        polys=f[1]; g=f[2]
        if polys:
            varint(len(polys),fb)
            for c,rr in polys:
                rq=[]
                for r in rr:
                    q=np.round(r.astype(np.float32)/Q).astype(np.int32); q=np.maximum(q,0)
                    keep=np.ones(len(q),bool); keep[1:]=(np.abs(np.diff(q,axis=0)).sum(1)>0); q=q[keep]
                    if len(q)>=3: rq.append(q)
                    elif not rq: break
                if not rq: rq=[np.array([[0,0],[0,0],[0,0]])]
                fb.append(int(c)); varint(len(rq),fb)
                for q in rq:
                    varint(len(q),fb); varint(q[0][0],fb); varint(q[0][1],fb)
                    dq=np.diff(q,axis=0)
                    for v in dq[:,0]: varint(zz(int(v)),fb)
                    for v in dq[:,1]: varint(zz(int(v)),fb)
    else:
        ref=k-f[1]; g=f[3]; assert ref!=0 and fr[f[1]][0]=='own'
        if f[2] is not None:
            assert len(f[2])==len(fr[f[1]][1]); fb+=bytes(f[2].tolist())
    grgb=np.clip(np.round(g[::-1]*100),0,255).astype(np.uint8)
    table+=bytes(grgb.tolist()); varint(zz(ref),table); varint(len(fb),table); body.append(bytes(fb))
head=bytearray([3]); varint(N,head); head.append(Q); head.append(K)
for c in cen: head+=bytes(np.clip(np.round(c[::-1]*180),0,255).astype(np.uint8).tolist())
blob=bytes(head)+bytes(table)+b''.join(body)
gz=gzip.compress(blob,9)
print('raw bytes',len(blob),'gz',len(gz),'b64',len(gz)*4//3)
A={'film':base64.b64encode(gz).decode(),'vig':vig,'pm':[round(float(x),2) for x in pm[::-1]],'vs':round(VS,4),
   'beats':[round(float(b),3) for b in beats],'media':mb,'dur':171.5,'poster':int(154.6*12),'titleK':int(tstart)}
open(S+'/app/assets.js','w').write('const A='+json.dumps(A,separators=(',',':'))+';')
src=open(S+'/app/app.src.html',encoding='utf-8').read()
assert src.count('/*__ASSETS__*/')==1
outp=r'C:\mathematicians-nightmare\mulberry-bush\index.html'
open(outp,'w',encoding='utf-8').write(src.replace('/*__ASSETS__*/',open(S+'/app/assets.js').read()))
print('wrote',outp,os.path.getsize(outp))
