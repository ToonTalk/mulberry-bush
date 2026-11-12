"""Capture two stretches of Round the Mulberry Bush at 30 frames a second, plus their sound rendered offline."""
import os, time, base64
from cdp import Page, S
p = Page(match='8765')
p.goto('http://localhost:8765/round/index.html')
time.sleep(2.5)
for i in range(40):
    if p.js("typeof scriptState==='function' && typeof cv!=='undefined'"): break
    time.sleep(0.5)

def frames(name, bp0, bp1):
    out = S + '/trailer/' + name; os.makedirs(out, exist_ok=True)
    n = int(round((bp1 - bp0) / 2 * 30))
    for i in range(n):
        bp = bp0 + i / 15.0
        # grain changes twelve times a second, as on the page
        change = 'true' if int(i * 12 / 30) != int((i - 1) * 12 / 30) else 'false'
        d = p.js("""(()=>{const s=scriptState(%r); s.omega=s.rate*TAU;
          lastGrainK=%s?-1:Math.floor(performance.now()/83);
          const was=playing; playing=true; render(s,1/30); playing=was;
          return cv.toDataURL('image/jpeg',0.93)})()""" % (bp, change))
        open('%s/%04d.jpg' % (out, i), 'wb').write(base64.b64decode(d.split(',')[1]))
    print(name, n, 'frames')

AUDIO = """(async()=>{
  const sr=44100, bp0=%d, bp1=%d, lead=0.05, tail=%f, ending=%s, spin=%s;
  const oc=new OfflineAudioContext(2, Math.ceil(sr*((bp1-bp0)/2+tail)), sr);
  band=new Band(oc);
  const T=bp=>lead+(bp-bp0)/2;
  // the wheel ticking on its pin, as on the page
  if(spin){band.whir.gain.setValueAtTime(0,T(48));band.whirSrc.playbackRate.setValueAtTime(.08,T(48));
    band.whir.gain.linearRampToValueAtTime(.0225,T(52));band.whirSrc.playbackRate.linearRampToValueAtTime(.54,T(52));
    band.whir.gain.linearRampToValueAtTime(0,T(52)+.3)}
  else{band.whir.gain.value=.045;
    band.whir.gain.setValueAtTime(.045,T(bp1)); band.whir.gain.linearRampToValueAtTime(0,T(bp1)+(ending?2.5:.3))}
  for(let s=bp0*3;s<bp1*3;s++) scheduleSlot(s, T(s/3), 1/6);
  if(ending){const when=T(bp1), bd=band;   // the piece's own last chord
    bd.acc(when,[36,48,55,60,64,67],1.7,.085);bd.fiddle(when,72,1.6,.12);bd.fiddle(when+.02,76,1.6,.09);[72,76,79,84].forEach((m,i)=>bd.glock(when+.5+i*.09,m+12,.14))}
  const buf=await oc.startRendering(), L=buf.getChannelData(0), R=buf.getChannelData(1), n=L.length;
  const i16=new Int16Array(n*2); for(let i=0;i<n;i++){i16[2*i]=Math.max(-1,Math.min(1,L[i]))*32767; i16[2*i+1]=Math.max(-1,Math.min(1,R[i]))*32767}
  const u8=new Uint8Array(i16.buffer); let s=''; for(let i=0;i<u8.length;i+=32768) s+=String.fromCharCode.apply(null,u8.subarray(i,i+32768));
  return btoa(s);
})()"""

def audio(name, bp0, bp1, tail, ending, spin):
    a = p.js(AUDIO % (bp0, bp1, tail, 'true' if ending else 'false', 'true' if spin else 'false'))
    open(S + '/trailer/%s.s16' % name, 'wb').write(base64.b64decode(a))
    print(name, 'audio bytes', len(a) * 3 // 4)

frames('roundA', 40, 52)
audio('roundA', 40, 52, 1.5, False, True)
