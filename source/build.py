"""Assemble the app from app.src.html + data/assets.js (the packed film).
Writes ../index.html (stand-alone page) and ../artifact/mulberry-bush-traced.html (fragment for publishing)."""
import os, re
here = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(here, 'app.src.html'), encoding='utf-8').read()
assert src.count('/*__ASSETS__*/') == 1
page = src.replace('/*__ASSETS__*/', open(os.path.join(here, 'data', 'assets.js'), encoding='utf-8').read())
open(os.path.join(here, '..', 'index.html'), 'w', encoding='utf-8').write(page)
frag = page
for tag in ('<!doctype html>\n', '<html lang="en">\n', '<head>\n', '</head>\n', '<body>\n', '</body>\n', '</html>\n',
            '<meta charset="utf-8">\n', '<meta name="viewport" content="width=device-width,initial-scale=1">\n'):
    assert frag.count(tag) == 1, tag
    frag = frag.replace(tag, '')
assert frag.count('<title>Mulberry Bush</title>') == 1
frag = frag.replace('<title>Mulberry Bush</title>', '<title>Mulberry Bush</title>\n<meta name="claude:viewport-fit-sides" content="cover">')
os.makedirs(os.path.join(here, '..', 'artifact'), exist_ok=True)
open(os.path.join(here, '..', 'artifact', 'mulberry-bush-traced.html'), 'w', encoding='utf-8').write(frag)
print('index.html', len(page), 'artifact', len(frag))
