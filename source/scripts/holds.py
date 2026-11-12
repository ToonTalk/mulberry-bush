import sys, numpy as np, warnings
warnings.filterwarnings('ignore')
S=sys.argv[1]; sys.path.insert(0,S+'/pylib')
import cv2
N=5240
prev=None; d=np.zeros(N+1)
for i in range(1,N+1):
    im=cv2.imread(f'{S}/all/f_{i:05d}.jpg',cv2.IMREAD_GRAYSCALE)
    sm=cv2.resize(im,(270,200),interpolation=cv2.INTER_AREA).astype(np.float32)
    sm=cv2.GaussianBlur(sm,(0,0),1.5)
    if prev is not None: d[i]=np.abs(sm-prev).mean()
    prev=sm
np.save(S+'/diff.npy',d)
for a in (240,420,1650,2700,3000):
    print(a, ' '.join(f'{v:.1f}' for v in d[a:a+45]))
