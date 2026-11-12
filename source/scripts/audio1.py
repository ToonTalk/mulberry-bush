import sys, wave, numpy as np
sys.path.insert(0, sys.argv[1]+'/pylib')
from scipy import signal
w=wave.open(sys.argv[1]+'/audio.wav'); n=w.getnframes(); sr=w.getframerate()
x=np.frombuffer(w.readframes(n),dtype=np.int16).astype(float)/32768
hop=256; nfft=4096
f,t,Z=signal.stft(x,sr,nperseg=nfft,noverlap=nfft-hop,window='hann')
M=np.abs(Z)
# onset strength: spectral flux on log-mag
L=np.log1p(50*M)
flux=np.maximum(0,np.diff(L,axis=1)).sum(0)
flux=flux-signal.medfilt(flux,31); flux=np.maximum(flux,0)
fr=sr/hop
# tempo autocorrelation
ac=np.correlate(flux,flux,'full')[len(flux)-1:]
lags=np.arange(len(ac))/fr
best=[]
for bpm in np.arange(50,260,0.5):
    lag=60/bpm*fr; i=int(round(lag)); best.append((ac[i]+0.5*ac[int(round(2*lag))]+0.33*ac[int(round(3*lag))]+0.25*ac[int(round(4*lag))],bpm))
best.sort(reverse=True)
print('tempo candidates',[(round(b,1),round(s)) for s,b in best[:12]])
# melody salience
fmin=180; nb=60  # semitone bins from ~F#3
mid0=54
def sal(col):
    out=np.zeros(nb)
    for k in range(nb):
        f0=440*2**((mid0+k-69)/12)
        s=0
        for h,wgt in enumerate([1,0.8,0.6,0.5,0.4],1):
            b=f0*h/(sr/nfft); bi=int(round(b))
            if bi<len(col)-1: s+=wgt*max(col[bi-1:bi+2])
        out[k]=s
    return out
names=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
step=int(0.1*fr)
seq=[]
for i in range(0,M.shape[1]-step,step):
    col=M[:,i:i+step].mean(1)
    s=sal(col); k=int(np.argmax(s)); seq.append((round(t[i],1),names[(mid0+k)%12]+str((mid0+k)//12-1),round(float(s[k])*1000)))
for a in range(0,len(seq),10):
    print(seq[a][0], ' '.join(f"{p}" for _,p,_ in seq[a:a+10]))
np.save(sys.argv[1]+'/flux.npy',flux)
