"""Builds the making-of report from report/report.src.html.

  ../report/index.html        standalone page, images loaded from report/img/
  ../artifact/making-of.html  publishable fragment with the images embedded
"""
import base64, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
src = open(os.path.join(ROOT, 'report', 'report.src.html'), encoding='utf-8').read()

# standalone copy: wrap the fragment in a document
head_end = src.index('</style>') + len('</style>')
standalone = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
              '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
              + src[:head_end] + '\n</head>\n<body style="margin:0">\n' + src[head_end:] + '\n</body>\n</html>\n')
open(os.path.join(ROOT, 'report', 'index.html'), 'w', encoding='utf-8').write(standalone)

# artifact copy: embed every image
n = 0
def embed(m):
    global n
    data = open(os.path.join(ROOT, 'report', m.group(1).replace('/', os.sep)), 'rb').read()
    n += 1
    return 'src="data:image/jpeg;base64,' + base64.b64encode(data).decode() + '"'
art = re.sub(r'src="(img/[^"]+\.jpg)"', embed, src)
assert n == 15, n
assert 'src="img/' not in art
out = os.path.join(ROOT, 'artifact', 'making-of.html')
open(out, 'w', encoding='utf-8').write(art)
print('standalone', len(standalone), 'artifact', os.path.getsize(out), 'images', n)
