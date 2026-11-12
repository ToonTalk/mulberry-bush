"""Capture verse 16 of the traced page: one JPEG per drawing, and its soundtrack rendered offline."""
import os, time, json, base64
from cdp import Page, S
OUT = S + '/trailer/traced'; os.makedirs(OUT, exist_ok=True)
p = Page(match='8765')
for i in range(60):
    if p.js("typeof film!=='undefined' && !!film"): break
    time.sleep(0.5)
V = 16
b0, b1 = V * 16, V * 16 + 16
B = json.loads(p.js('JSON.stringify(Array.from(B))'))
json.dump(B, open(S + '/trailer/beats.json', 'w'))
k0, k1 = int(B[b0] * 12), int(B[b1] * 12) + 1
p.js("mode='film'")
for k in range(k0, k1 + 1):
    d = p.js("(drawFrame(%d), screen.toDataURL('image/jpeg',0.93))" % k)
    open('%s/k%05d.jpg' % (OUT, k), 'wb').write(base64.b64decode(d.split(',')[1]))
print('frames', k0, k1)

audio = p.js("""(async()=>{
  const sr=44100, b0=%d, b1=%d, lead=0.05, dur=(B[b1]-B[b0])+2.5;
  const oc=new OfflineAudioContext(2, Math.ceil(sr*dur), sr);
  mode='film'; band=new Band(oc); band.proj.gain.value=0.035;
  for(let s=b0*3;s<b1*3;s++){const b=(s/3)|0; scheduleSlot(s, lead+slotTime(s)-B[b0], (B[b+1]-B[b])/3)}
  const buf=await oc.startRendering(), L=buf.getChannelData(0), R=buf.getChannelData(1), n=L.length;
  const i16=new Int16Array(n*2); for(let i=0;i<n;i++){i16[2*i]=Math.max(-1,Math.min(1,L[i]))*32767; i16[2*i+1]=Math.max(-1,Math.min(1,R[i]))*32767}
  const u8=new Uint8Array(i16.buffer); let s=''; for(let i=0;i<u8.length;i+=32768) s+=String.fromCharCode.apply(null,u8.subarray(i,i+32768));
  return btoa(s);
})()""" % (b0, b1))
open(S + '/trailer/traced.s16', 'wb').write(base64.b64decode(audio))
print('audio bytes', len(audio) * 3 // 4, 'verse', B[b0], B[b1])
