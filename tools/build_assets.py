"""Convert client photos to WebP (thumb 600w + full 1800w) and write assets/manifest.json.
Usage: python tools/build_assets.py   (reads ../<client>/ folders, writes public_html/assets)"""
import os, re, json, sys
from PIL import Image, ImageOps, ImageFilter
try:
    from pillow_heif import register_heif_opener; register_heif_opener()
except Exception: pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.dirname(ROOT)
OUT = os.path.join(ROOT, 'public_html', 'assets')
EXT = {'.jpg', '.jpeg', '.png', '.heic'}

# Photos saved sideways without EXIF info: degrees counter-clockwise to turn them upright.
# Mrs. Poornima: hand-picked photos from poornima/Raw Photo (2 per area); sideways ones turned upright.
SRCDIR = {'poornima': os.path.join('poornima', 'Raw Photo')}
SELECT = {'poornima': ['183A0001.JPG', '183A0024.JPG', '183A0039.JPG', '183A0050.JPG', '183A0097.JPG',
                       '183A0090.JPG', '183A0114.JPG', '183A0149.JPG', '183A0137.JPG', '183A0146.JPG']}
SLUG = {'Mrs.Asha Narayan': 'Asha Narayan', 'KrishnaPriya': 'poornima', 'poornima': 'mrs-poornima'}
# client page order on the site (anything not listed goes last, alphabetical)
ORDER = ['mohan', 'asha-narayan', 'poornima', 'preethi-illam', 'priya-meghanathan', 'ramakrishnan', 'sunil', 'suraj', 'yogeshwari', 'mrs-poornima']
# Vimeo videos per client id (tools/videos.json), copied into the manifest
VIDEOS = json.load(open(os.path.join(ROOT, 'tools', 'videos.json'), encoding='utf-8'))
ROTATE = {('poornima', f): 90 for f in ('183A0090.JPG', '183A0149.JPG', '183A0146.JPG')}
ROTATE.update({('Mohan', f): 90 for f in ('183A0156.JPG','183A0158.JPG','183A0160.JPG','183A0210.JPG','183A0221.JPG','183A0230.JPG')})

# Display title (Mr./Mrs.) and builder per client. Folder name stays the client name; label = title + name.
# builder -> logos/builders/<id>.svg with its width/height (for layout). None = individual house.
BUILDERS = {'brigade': (89, 102, 'svg'), 'ayana': (316, 169, 'svg'), 'florence': (130, 58, 'png')}
META = {
    'Mohan': ('Mr.', None), 'Suraj': ('Mr.', None), 'Preethi Illam': ('', None),
    'KrishnaPriya': ('Mrs.', 'brigade'), 'poornima': ('Mrs.', None), 'Yogeshwari': ('Mrs.', 'brigade'), 'Ramakrishnan': ('Mr.', 'brigade'),
    'Priya Meghanathan': ('Mrs.', 'ayana'), 'Sunil': ('Mr.', None),
    'Mrs.Asha Narayan': ('Mrs.', 'florence'),
}
COVER = {'Mrs.Asha Narayan': 'L1.png', 'poornima': '183A0114.JPG'}   # tile cover when it should not be the first photo (gallery order is unchanged)
DISPLAY = {'Mrs.Asha Narayan': 'Asha Narayan', 'poornima': 'Poornima'}   # shown name when it differs from the folder name

def nat(s): return [int(t) if t.isdigit() else t.lower() for t in re.split(r'(\d+)', s)]
def slug(s): return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', s.lower())).strip('-')

LOGO = Image.open(os.path.join(ROOT, 'logos', 'jomo-logo-white.png')).convert('RGBA')
LOGO = LOGO.crop(LOGO.getbbox())

def watermark(im):
    """JOMO Home Interiors logo, bottom-right, ~22% of the width, soft shadow so it reads on light and dark walls."""
    w = max(60, round(im.width * 0.22)); h = round(LOGO.height * w / LOGO.width)
    lg = LOGO.resize((w, h), Image.LANCZOS)
    a = lg.getchannel('A').point(lambda v: int(v * 0.75)); lg.putalpha(a)
    sh = Image.new('RGBA', lg.size, (0, 0, 0, 0)); sh.putalpha(lg.getchannel('A').point(lambda v: int(v * 0.6)))
    sh = sh.filter(ImageFilter.GaussianBlur(max(1, w // 60)))
    m = round(im.width * 0.03)
    base = im.convert('RGBA'); pos = (im.width - w - m, im.height - h - m)
    base.alpha_composite(sh, pos); base.alpha_composite(lg, pos)
    return base.convert('RGB')

def save(im, path, width, q, max_kb=None):
    im = im.copy()
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im = watermark(im)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    while True:
        im.save(path, 'WEBP', quality=q, method=6)
        if not max_kb or os.path.getsize(path) <= max_kb * 1024 or q <= 40: break
        q -= 5
    return im.width, im.height

manifest = []
for client in sorted(os.listdir(SRC), key=nat):
    d = os.path.join(SRC, SRCDIR.get(client, client))
    if not os.path.isdir(d) or client == os.path.basename(ROOT): continue
    files = sorted((f for f in os.listdir(d) if os.path.splitext(f)[1].lower() in EXT), key=nat)
    if client in SELECT: files = [f for f in SELECT[client] if f in files]
    if not files: continue
    cs, imgs, used = slug(SLUG.get(client, client)), [], set()
    for f in files:
        name = slug(os.path.splitext(f)[0]) or 'img'
        while name in used: name += '-x'
        used.add(name)
        im = ImageOps.exif_transpose(Image.open(os.path.join(d, f)))
        if (client, f) in ROTATE: im = im.rotate(ROTATE[(client, f)], expand=True)
        im = im.convert('RGBA' if im.mode in ('RGBA', 'LA', 'P') else 'RGB')
        tw, th = save(im, f'{OUT}/{cs}/thumb/{name}.webp', 600, 75, 60)
        fw, fh = save(im, f'{OUT}/{cs}/full/{name}.webp', 1800, 80)
        imgs.append({'n': name, 'tw': tw, 'th': th, 'fw': fw, 'fh': fh})
    title, b = META.get(client, ('', None))
    manifest.append({'id': cs, 'name': client, 'label': (title + ' ' + DISPLAY.get(client, client)).strip(), 'cover': (slug(os.path.splitext(COVER[client])[0]) if client in COVER else imgs[0]['n']),
                     'builder': {'f': b, 'w': BUILDERS[b][0], 'h': BUILDERS[b][1], 'e': BUILDERS[b][2]} if b else None, 'videos': VIDEOS.get(cs, []), 'images': imgs})
    print(client, len(imgs), flush=True)
manifest.sort(key=lambda c: ORDER.index(c['id']) if c['id'] in ORDER else len(ORDER))
import shutil
os.makedirs(f'{OUT}/builders', exist_ok=True)
for b in BUILDERS: shutil.copy(os.path.join(ROOT, 'logos', 'builders', f'{b}.{BUILDERS[b][2]}'), f'{OUT}/builders/{b}.{BUILDERS[b][2]}')
with open(f'{OUT}/manifest.json', 'w', encoding='utf-8') as fh:
    json.dump(manifest, fh, ensure_ascii=False, separators=(',', ':'))
