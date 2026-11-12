"""Compose the 30-second trailer: bits of the 1976 film, the traced page, and Round the Mulberry Bush."""
import sys, os, json, subprocess, glob
S = 'C:/Users/toont/AppData/Local/Temp/claude/2adc7078fe966463/ae6463b0-0602-40b5-a822-8d90e035db45/scratchpad'
sys.path.insert(0, S + '/pylib')
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
T = S + '/trailer'
FF = S + '/ffmpeg.exe'
OUT = sys.argv[1] if len(sys.argv) > 1 else T + '/trailer.mp4'
W, H, FPS, DUR, SR = 1280, 960, 30, 30.0, 44100
N = int(DUR * FPS)
B = json.load(open(T + '/beats.json'))

# ---------- the cut ----------
A0 = 36                       # sound of segment 1: verse 2, beats 4-16 of the original recording
SRC = [36, 37, 38, 39,  148, 149, 150, 151,  176, 177, 178, 179]   # pictures: paint, stripes, big circles
V = 256                       # segment 2: verse 16, traced
t1 = B[A0 + 12] - B[A0]
t2 = B[V + 16] - B[V]
T2, TA, TB, TE = t1, t1 + t2, t1 + t2 + 6, t1 + t2 + 12
print('cut points', round(T2, 3), round(TA, 3), round(TB, 3), round(TE, 3))

# ---------- film frames ----------
GATE = (27, 158, 1051, 908)
def film_time_seg1(t):
    tt = B[A0] + t
    j = max(0, min(11, next((i for i in range(12) if tt < B[A0 + i + 1]), 11)))
    f = (tt - B[A0 + j]) / (B[A0 + j + 1] - B[A0 + j])
    return B[SRC[j]] + f * (B[SRC[j] + 1] - B[SRC[j]])
need = set()
for i in range(N):
    t = i / FPS
    if t < T2: need.add(int(film_time_seg1(t) * 30))
    elif t < T2 + 1.6: need.add(int((B[V] + t - T2) * 30))
need = sorted(need)
film = {}
cap = cv2.VideoCapture(S + '/film.mp4')
needset = set(need)
for idx in range(need[-1] + 1):          # step forward through the film: seeking is slow and unreliable on this file
    if not cap.grab(): break
    if idx in needset:
        ok, fr = cap.retrieve()
        x0, y0, x1, y1 = GATE
        film[idx] = cv2.cvtColor(fr[y0:y1, x0:x1], cv2.COLOR_BGR2RGB)
print('film frames', len(film))

def fit_gate(img):            # 1024x750 picture -> 1280x938, centred
    out = np.zeros((H, W, 3), np.uint8)
    r = cv2.resize(img, (1280, 938), interpolation=cv2.INTER_LANCZOS4)
    out[11:949] = r
    return out
def fit_round(img):           # 1000x820 stage -> 1171x960, centred
    out = np.zeros((H, W, 3), np.uint8); out[:] = (4, 2, 4)
    r = cv2.resize(img, (1171, 960), interpolation=cv2.INTER_LANCZOS4)
    out[:, 54:54 + 1171] = r
    return out
def load(path):
    return np.asarray(Image.open(path).convert('RGB'))
cache = {}
def cached(key, fn):
    if key not in cache:
        if len(cache) > 6: cache.pop(next(iter(cache)))
        cache[key] = fn()
    return cache[key]

# ---------- captions ----------
HAND = 'C:/Windows/Fonts/segoepr.ttf'; HANDB = 'C:/Windows/Fonts/segoeprb.ttf'
INK = (250, 232, 241)
def caption(lines, anchor, xy, spacing=6):
    """lines: [(text, size, bold)] -> RGBA layer the size of the frame, with a soft dark shadow."""
    fonts = [ImageFont.truetype(HANDB if b else HAND, s) for _, s, b in lines]
    dm = ImageDraw.Draw(Image.new('L', (8, 8)))
    boxes = [dm.textbbox((0, 0), txt, font=f) for (txt, _, _), f in zip(lines, fonts)]
    ws = [b[2] - b[0] for b in boxes]; hs = [int(f.size * 1.32) for f in fonts]
    tw, th = max(ws), sum(hs) + spacing * (len(lines) - 1)
    x, y = xy
    if anchor == 'bl': y = y - th
    if anchor == 'c': x, y = x - tw // 2, y - th // 2
    text = Image.new('L', (W, H), 0); d = ImageDraw.Draw(text); yy = y
    for (txt, _, _), f, w, h, bx in zip(lines, fonts, ws, hs, boxes):
        xx = x + (tw - w) // 2 if anchor == 'c' else x
        d.text((xx - bx[0], yy), txt, font=f, fill=255); yy += h + spacing
    sh = text.filter(ImageFilter.GaussianBlur(9)).point(lambda v: min(255, int(v * 2.6)))
    sh2 = text.filter(ImageFilter.GaussianBlur(2.2)).point(lambda v: min(255, int(v * 1.6)))
    shadow = np.maximum(np.asarray(sh, np.float32) * .8, np.asarray(sh2, np.float32) * .9) / 255
    return shadow[..., None], np.asarray(text, np.float32)[..., None] / 255
def fade(t, a, b, f=.35):
    return float(np.clip(min((t - a) / f, (b - t) / f), 0, 1))
CAPS = [
    (0.7, T2 - .25, caption([('MULBERRY BUSH', 74, True), ('a film by Ken Kahn, 1976', 36, False)], 'bl', (66, H - 64))),
    (T2 + .3, T2 + 3.7, caption([('every drawing, traced', 46, True)], 'bl', (66, H - 70))),
    (T2 + 4.0, TA - .3, caption([('redrawn live in the browser', 46, True), ('with a new band on the old beat', 34, False)], 'bl', (66, H - 64))),
    (TA + .4, TA + 2.9, caption([('ROUND THE MULBERRY BUSH', 40, True)], 'c', (W // 2, H - 42))),
    (TA + 3.2, TB - .25, caption([('four dancers round a backlit screen', 32, True)], 'c', (W // 2, H - 42))),
    (TB + .35, TB + 2.8, caption([('then the dance again, on a spinning paper wheel', 30, True)], 'c', (W // 2, H - 42))),
    (TB + 3.1, TE - .3, caption([('nothing traced  ·  turn the wheel yourself', 32, True)], 'c', (W // 2, H - 42))),
    (TE + .5, DUR - .45, caption([('MULBERRY BUSH', 88, True), ('the 1976 film  ·  traced  ·  reimagined', 34, False), (' ', 14, False),
                                  ('toontalk.github.io/mulberry-bush', 40, True)], 'c', (W // 2, H // 2 - 10), 10)),
]

# ---------- frames ----------
def frame(i):
    t = i / FPS
    if t < T2:                                            # the film itself
        img = fit_gate(film[int(film_time_seg1(t) * 30)]).astype(np.float32)
        img *= np.clip(t / .8, 0, 1)
    elif t < TA:                                          # the traced page, wiped in over the film
        tf = B[V] + (t - T2); k = int(tf * 12)
        img = cached(('k', k), lambda: fit_gate(load('%s/traced/k%05d.jpg' % (T, k)))).astype(np.float32)
        u = (t - T2 - .3) / 1.0
        if u < 1:
            u = max(0.0, u); u = u * u * (3 - 2 * u); xw = int(u * W)
            old = fit_gate(film[int(tf * 30)]).astype(np.float32)
            img = img.copy(); img[:, xw:] = old[:, xw:]
            if 0 < xw < W: img[:, max(0, xw - 2):xw + 2] = (250, 232, 241)
        d = (TA - t) / .2                                 # short dip into the wheel
        if d < 1: img = img * max(0.0, d)
    elif t < TE:
        name, tt = ('roundA', t - TA) if t < TB else ('roundB', t - TB)
        j = min(179, int(round(tt * FPS)))
        img = fit_round(load('%s/%s/%04d.jpg' % (T, name, j))).astype(np.float32)
        if t < TB: img *= np.clip((t - TA) / .2 + .0, 0, 1)
    else:                                                 # end card over the wheel, dimmed
        j = min(119, int(round((t - TE) * FPS)))
        img = fit_round(load('%s/roundE/%04d.jpg' % (T, j))).astype(np.float32)
        img *= 1 - .72 * np.clip((t - TE) / .6, 0, 1)
    for a, b, (shadow, text) in CAPS:
        op = fade(t, a, b)
        if op > 0:
            img = img * (1 - shadow * op * .85)
            img = img * (1 - text * op) + np.array(INK, np.float32) * text * op
    img *= np.clip((DUR - t) / .45, 0, 1)                 # fade out
    return np.clip(img, 0, 255).astype(np.uint8)

if len(sys.argv) > 2 and sys.argv[2] == 'dbg':
    ims = [Image.fromarray(frame(i)).resize((320, 240)) for i in range(0, 180, 9)]
    sheet = Image.new('RGB', (320 * 10, 240 * 2))
    for n, im in enumerate(ims): sheet.paste(im, ((n % 10) * 320, (n // 10) * 240))
    sheet.save(T + '/dbg.jpg', quality=82); print('dbg written', [round(film_time_seg1(i / 30), 2) for i in range(0, 180, 9)]); sys.exit()
if len(sys.argv) > 2 and sys.argv[2] == 'stills':
    ts = [0.4, 2.5, 4.3, 5.7, T2 + .7, T2 + 1.0, T2 + 5, TA + 1.5, TA + 4.5, TB + 1.5, TB + 4.5, TE + 2]
    ims = [Image.fromarray(frame(int(t * FPS))).resize((480, 360)) for t in ts]
    sheet = Image.new('RGB', (480 * 4, 360 * 3))
    for n, im in enumerate(ims): sheet.paste(im, ((n % 4) * 480, (n // 4) * 360))
    sheet.save(T + '/stills.jpg', quality=85); print('stills written'); sys.exit()

# ---------- sound ----------
def s16(path):
    return np.frombuffer(open(path, 'rb').read(), np.int16).astype(np.float32).reshape(-1, 2) / 32768
subprocess.run([FF, '-y', '-v', 'error', '-ss', '%.3f' % B[A0], '-t', '%.3f' % (t1 + .6), '-i', S + '/film.mp4',
                '-vn', '-ac', '2', '-ar', str(SR), '-f', 's16le', T + '/orig.s16'], check=True)
mix = np.zeros((int(DUR * SR), 2), np.float32)
def rms(x): return float(np.sqrt(np.mean(x ** 2)) + 1e-9)
def place(x, start, body, fin, fout, target=.105, lead=0.0):
    """x starts at `start` seconds (minus lead); stays full for `body` seconds, then fades over fout."""
    x = x[int(lead * SR):] if lead else x
    n = min(len(x), int((body + fout) * SR), len(mix) - int(start * SR))
    x = x[:n].copy()
    x *= target / rms(x[:int(body * SR)])
    env = np.ones(n, np.float32)
    k = int(fin * SR)
    if k: env[:k] = np.linspace(0, 1, k) ** 2
    b0 = int(body * SR)
    if b0 < n: env[b0:] = np.linspace(1, 0, n - b0) ** 2
    i0 = int(start * SR); mix[i0:i0 + n] += x * env[:, None]
place(s16(T + '/orig.s16'), 0, t1, .7, .35, target=.095)
place(s16(T + '/traced.s16'), T2, t2, 0, .5, lead=.05)
place(s16(T + '/roundA.s16'), TA, 6, 0, .45, lead=.05)
place(s16(T + '/roundB.s16'), TB, DUR - TB - .6, 0, .6, lead=.05)
pk = float(np.abs(mix).max()); print('mix peak before', round(pk, 3))
mix *= .84 / pk
for a, b in ((0, T2), (T2, TA), (TA, TB), (TB, TE), (TE, DUR)):
    seg = mix[int(a * SR):int(b * SR)]; print('  %5.2f-%5.2f rms %.3f peak %.3f' % (a, b, rms(seg), np.abs(seg).max()))
import wave
w = wave.open(T + '/mix.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()

# ---------- encode ----------
os.makedirs(os.path.dirname(OUT), exist_ok=True)
enc = subprocess.Popen([FF, '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H), '-r', str(FPS), '-i', '-',
                        '-i', T + '/mix.wav', '-c:v', 'libx264', '-preset', 'slow', '-crf', '22', '-pix_fmt', 'yuv420p',
                        '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-shortest', OUT], stdin=subprocess.PIPE)
for i in range(N):
    enc.stdin.write(frame(i).tobytes())
enc.stdin.close(); enc.wait()
print('wrote', OUT, os.path.getsize(OUT), 'bytes')
