import sys,glob,pickle,time
from common import *
import repack
eps=float(sys.argv[1]); i=int(sys.argv[2]); n=int(sys.argv[3])
if i<0:
    cen=repack.make_palette(repack.load_raw()); np.save(S+'/pal.npy',cen); print('palette',len(cen)); sys.exit()
cen=np.load(S+'/pal.npy')
files=(sorted(glob.glob(S+'/raw_*.pkl'))+sorted(glob.glob(S+'/dimraw_*.pkl')))
res={}
for j,fn in enumerate(files):
    if j%n!=i: continue
    raw=pickle.load(open(fn,'rb')); dimf='dimraw' in fn
    for k,(polys,g,vf) in raw.items(): res[k]=(repack.clean(polys,g,cen,eps),g,dimf)
pickle.dump(res,open(S+f'/clean_part_{i}.pkl','wb'))
