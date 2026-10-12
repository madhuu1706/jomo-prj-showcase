# JOMO Home Interiors – client portfolio website

Single public portfolio sent to prospective clients as a reference. No logins, no database.

## Current state (updated)
- REAL images are wired in. Upload the contents of `public_html/` (index.html, assets/, .htaccess) to Hostinger public_html.
- Rebuild after adding/changing photos: `python tools/build_assets.py` then `python tools/build_site.py` (reads ../<Client>/ folders, natural filename order, first image = cover). Needs Pillow.
- Client page = name (gold) + thumb gallery + lightbox (full webp). Walkthrough/Shoot/Video sections were removed per owner.
- Old sample-data notes below are historical.

## Previous state
- `index.html` = the finished design with 8 SAMPLE clients and drawn placeholder pictures (self-contained, logo embedded).
- `source/template.html` = editable source; placeholders @@LOGO_LIGHT@@ / @@LOGO_DARK@@ / @@LOGO_GOLD@@ are replaced by the base64 files in `source/` to produce index.html.
- `logos/` = original navy logo, plus gold and white recolours.

## Design decisions (from the owner – keep)
- Colours: navy + gold only (palette from the JOMO ERP console: navy #152238, #1c2f4d, gold #d8ad5f). No beige, no light theme.
- Header: navy bar with GOLD logo (original navy logo is invisible on navy).
- Home: tile = cover image + client name (gold). No counts, no type/location/year, no filters, no stats row, no footer text. Hero: "Crafting homes where you belong."
- Mobile: all 8 tiles with names visible on the first screen with no scrolling, 3 tiles per row. Laptop: small tiles (5 per row).
- Client page: client name (gold) then directly under it pill buttons (not a dropdown): Walkthrough, Project Shoot, Images, Video. Click scrolls to that section. Section headings gold, no counts/descriptions. Lightbox for photos/videos.
- No fake "JOMO" watermark on images.

## Next steps
1. Put real media in `assets/<client>/{walkthrough,shoot,images,video}`; optimise: photos -> WebP (thumb + full), videos -> compressed MP4 + poster image. Lazy-load, small previews first.
2. Replace the sample CLIENTS list (function loadClients in index.html) with real clients pointing to those files (relative paths). Keep it a static manifest; no database needed.
3. Host on Hostinger (upload index.html + assets/ into public_html). Check total media size vs plan disk space (Web Single 10 GB, Premium 20 GB). Option: unlisted YouTube for videos.
4. Test on a phone-width screen (390px) that all tiles still fit on first screen.
