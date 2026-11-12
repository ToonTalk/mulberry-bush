import sys, wave, numpy as np, warnings
warnings.filterwarnings('ignore')
sys.path.insert(0, sys.argv[1]+'/pylib')
from scipy import signal
w=wave.open(sys.argv[1]+'/audio.wav'); n=w.getnframes(); sr=w.getframerate()
x=np.frombuffer(w.readframes(n),dtype=np.int16).astype(float)/32768
hop=256; nfft=4096
f,t,Z=signal.stft(x,sr,nperseg=nfft,noverlap=nfft-hop,window='hann')
M=np.abs(Z); fr=sr/hop
flux=np.load(sys.argv[1]+'/flux.npy'); flux=flux/flux.std()
# DP beat tracking (Ellis)
period=60/120.2*fr
N=len(flux); score=flux.copy(); back=-np.ones(N,int); alpha=400
for i in range(N):
    lo=int(i-2*period); hi=int(i-period/2)
    if hi<=0: continue
    lo=max(lo,0); pr=np.arange(lo,hi)
    pen=-alpha*(np.log((i-pr)/period))**2
    c=score[pr]+pen; j=int(np.argmax(c)); score[i]=flux[i]+c[j]; back[i]=pr[j]
i=int(np.argmax(score[-int(period*8):]))+N-int(period*8); beats=[]
while i>=0: beats.append(i); i=back[i]
beats=np.array(beats[::-1])/fr
print('nbeats',len(beats),'first',beats[:6].round(2),'last',beats[-4:].round(2))
ib=np.diff(beats)
for a in range(0,len(ib),32): print(round(beats[a],1),'bpm',round(60/ib[a:a+32].mean(),2))
# chroma per beat
names=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
def chroma(a,b):
    i0=int(a*fr); i1=max(i0+1,int(b*fr)); col=M[:,i0:i1].mean(1); ch=np.zeros(12)
    for bi in range(int(100/(sr/nfft)),int(2000/(sr/nfft))):
        fq=bi*sr/nfft; m=int(round(69+12*np.log2(fq/440)))%12; ch[m]+=col[bi]**2
    return ch/ch.sum()
lab=[]
for a,b in zip(beats[:-1],beats[1:]):
    ch=chroma(a,b)
    Cs=ch[0]+ch[4]+ch[7]*0.5; Gs=ch[2]+ch[11]+ch[5]+ch[7]*0.5
    lab.append('C' if Cs>Gs else 'G')
s=''.join(lab); 
for a in range(0,len(s),16): print(round(beats[a],2), s[a:a+16])
# energy per beat (to see where music starts/stops)
np.save(sys.argv[1]+'/beats.npy',beats)
# best phase of 16-beat pattern
pat='CCCCGGGGCCCCGGCC'
for ph in range(16):
    sc=sum(1 for i,c in enumerate(s) if c==pat[(i+ph)%16]); print(ph,sc,end=' | ')
