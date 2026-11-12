"""Write ../round/index.html (stand-alone) and ../artifact/round-the-mulberry-bush.html (fragment for publishing) from ../round/round.src.html."""
import os
here = os.path.dirname(os.path.abspath(__file__))

def icon_link(name):
    """<link> tag carrying source/favicons/<name>.svg as a data URI (stand-alone pages only)."""
    from urllib.parse import quote
    svg = open(os.path.join(here, 'favicons', name + '.svg'), encoding='utf-8').read().strip()
    return '<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,' + quote(svg, safe="/:='") + '">'
page = open(os.path.join(here, '..', 'round', 'round.src.html'), encoding='utf-8').read()
T = '<title>Round the Mulberry Bush</title>'
assert page.count(T) == 1
open(os.path.join(here, '..', 'round', 'index.html'), 'w', encoding='utf-8').write(page.replace(T, T + '\n' + icon_link('round')))
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
