import sys, os, numpy as np, warnings
warnings.filterwarnings('ignore')
S=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,S+'/pylib')
import cv2
X0,Y0,W,H=27,158,1024,750
def crop(im): return im[Y0:Y0+H,X0:X0+W]
class Film:
    def __init__(s):
        s.cap=cv2.VideoCapture(S+'/film.mp4'); s.pos=-1
    def frame(s,i):
        if s.pos<i<=s.pos+60:
            for _ in range(i-s.pos-1): s.cap.grab()
        elif i!=s.pos+1: s.cap.set(cv2.CAP_PROP_POS_FRAMES,i)
        ok,im=s.cap.read(); s.pos=i
        return crop(im).astype(np.float32) if ok else None
def get_plate():
    p=S+'/plate.npy'
    if os.path.exists(p): return np.load(p)
    f=Film(); acc=[]
    for i in range(200,4500,14):
        acc.append(cv2.GaussianBlur(f.frame(i),(0,0),2).astype(np.uint8))
    m=np.median(np.array(acc),axis=0).astype(np.float32)
    m=cv2.GaussianBlur(m,(0,0),6)
    np.save(p,m); return m
def ratio(im,plate):
    # per-channel robust gain then ratio
    b=cv2.GaussianBlur(im,(0,0),1.2)
    r=b/np.maximum(plate,1)
    g=np.median(r.reshape(-1,3)[::37],axis=0)
    return r/g, g
def inkmask(R,thr=0.2):
    d=1-R.min(2)
    return d>thr, d
