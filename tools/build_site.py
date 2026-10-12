"""Build public_html/index.html from source/template.html + assets/manifest.json (run build_assets.py first)."""
import os, json, shutil
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(R, 'public_html')
m = open(f'{P}/assets/manifest.json', encoding='utf-8').read()
t = open(f'{R}/source/template.html', encoding='utf-8').read().replace('@@MANIFEST@@', m)
open(f'{P}/index.html', 'w', encoding='utf-8').write(t)
shutil.copy(f'{R}/logos/jomo-logo-gold.png', f'{P}/assets/logo.png')
