"""Build one self-contained HTML file with every image embedded (base64). Run after build_assets.py + build_site.py."""
import os, base64, json
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A = f'{R}/public_html/assets'
h = open(f'{R}/public_html/index.html', encoding='utf-8').read()
b64 = lambda p: base64.b64encode(open(p, 'rb').read()).decode()
parts = []
for c in json.load(open(f'{A}/manifest.json', encoding='utf-8')):
    for i in c['images']:
        for k in ('thumb', 'full'):
            parts.append(f'"{c["id"]}/{k}/{i["n"]}":"data:image/webp;base64,{b64(f"{A}/{c["id"]}/{k}/{i["n"]}.webp")}"')
old_t = "const thumb = (c,i) => `${A}${c.id}/thumb/${i.n}.webp`;"
old_f = "const full  = (c,i) => `${A}${c.id}/full/${i.n}.webp`;"
assert old_t in h and old_f in h
h = h.replace(old_t, "const thumb = (c,i) => IMG[`${c.id}/thumb/${i.n}`];").replace(old_f, "const full  = (c,i) => IMG[`${c.id}/full/${i.n}`];")
h = h.replace("const CLIENTS =", "const IMG = {" + ",".join(parts) + "};\nconst CLIENTS =", 1)
h = h.replace("url(assets/logo.png)", f"url(data:image/png;base64,{b64(A + '/logo.png')})")
h = h.replace('<link rel="icon" href="assets/logo.png">', f'<link rel="icon" href="data:image/png;base64,{b64(A + "/logo.png")}">')
open(f'{R}/JOMO-Portfolio-single.html', 'w', encoding='utf-8').write(h)
