"""Write ../round/index.html (stand-alone) and ../artifact/round-the-mulberry-bush.html (fragment for publishing) from ../round/round.src.html."""
import os
here = os.path.dirname(os.path.abspath(__file__))
page = open(os.path.join(here, '..', 'round', 'round.src.html'), encoding='utf-8').read()
open(os.path.join(here, '..', 'round', 'index.html'), 'w', encoding='utf-8').write(page)
frag = page
for tag in ('<!doctype html>\n', '<html lang="en">\n', '<head>\n', '</head>\n', '<body>\n', '</body>\n', '</html>\n',
            '<meta charset="utf-8">\n', '<meta name="viewport" content="width=device-width,initial-scale=1">\n'):
    assert frag.count(tag) == 1, tag
    frag = frag.replace(tag, '')
t = '<title>Round the Mulberry Bush</title>'
assert frag.count(t) == 1
frag = frag.replace(t, t + '\n<meta name="claude:viewport-fit-sides" content="cover">')
os.makedirs(os.path.join(here, '..', 'artifact'), exist_ok=True)
open(os.path.join(here, '..', 'artifact', 'round-the-mulberry-bush.html'), 'w', encoding='utf-8').write(frag)
print('round/index.html', len(page), 'artifact', len(frag))
