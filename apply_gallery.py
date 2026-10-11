"""Usage: put raw generated images at /workspace/gallery-raw/g1..g7.(png|jpg|webp), then:
   python3 /workspace/photobooth-site/apply_gallery.py
Optimizes to gallery/gN.jpg (max 1400px, q82), swaps the .ph placeholders in index.html for <img> tiles,
updates the gallery note, and renders preview-gallery-desktop.png / preview-gallery-mobile.png.
Does NOT deploy."""
import glob, pathlib, re, sys
from PIL import Image
SITE = pathlib.Path("/workspace/photobooth-site"); RAW = pathlib.Path("/workspace/gallery-raw")
# tile order in the grid: (classes, alt)
TILES = [
 ("big",  "Elegant photobooth with a gold sequin backdrop and cream and gold balloon garland at a home birthday party"),
 ("",     "Kids in party hats laughing with fun photobooth props"),
 ("",     "Hand holding a printed photo strip at a birthday party"),
 ("wide", "Photobooth prop table with glasses, crowns, masks and balloons"),
 ("",     "Adults celebrating a milestone birthday at an evening party with a booth backdrop and fairy lights"),
 ("",     "Close-up of custom birthday photo prints on a gold tray"),
 ("wide", "Villa garden party in Dubai with a photobooth and a cream and gold balloon arch"),
]
out = SITE / "gallery"; out.mkdir(exist_ok=True)
for i in range(1, len(TILES) + 1):
    src = [p for p in glob.glob(str(RAW / f"g{i}.*"))]
    if not src: sys.exit(f"missing raw image g{i}")
    im = Image.open(src[0]).convert("RGB"); im.thumbnail((1400, 1400), Image.LANCZOS)
    im.save(out / f"g{i}.jpg", "JPEG", quality=82, optimize=True, progressive=True)
html = (SITE / "index.html").read_text()
imgs = "\n".join(
    f'        <figure class="gi{(" " + c) if c else ""}"><img src="gallery/g{i}.jpg" alt="{a}" loading="lazy" decoding="async"></figure>'
    for i, (c, a) in enumerate(TILES, 1))
html, n = re.subn(r'(<div class="gallery-grid">\n)(?:\s*<div class="ph[^"]*"><span>Your photos here</span></div>\n)+',
                  lambda m: m.group(1) + imgs + "\n", html)
assert n == 1, "placeholder block not found"
html = html.replace("<!-- GALLERY (placeholders) -->", "<!-- GALLERY -->")
html = re.sub(r'\s*<!-- ✏️ Replace each \.ph block.*?-->', "", html)
html = html.replace('Follow us on <a class="js-fb"', 'See more on our <a class="js-fb"').replace(
    'Facebook</a> for photos from our latest parties.', 'Facebook</a> page.')
css = ("  .gi{margin:0;border-radius:14px;overflow:hidden;background:#efe6d8}\n"
       "  .gi img{width:100%;height:100%;object-fit:cover;display:block}\n"
       "  .gi.big{grid-column:span 2;grid-row:span 2}\n  .gi.wide{grid-column:span 2}\n")
html = html.replace("  .gallery-note{", css + "  .gallery-note{", 1)
(SITE / "index.html").write_text(html)
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, w, dsf in [("desktop", 1280, 1), ("mobile", 390, 2)]:
        pg = b.new_page(viewport={"width": w, "height": 900}, device_scale_factor=dsf)
        pg.goto((SITE / "index.html").as_uri(), wait_until="networkidle")
        pg.evaluate("document.querySelectorAll('#gallery img').forEach(i=>i.loading='eager')")
        pg.wait_for_function("[...document.querySelectorAll('#gallery img')].every(i=>i.complete&&i.naturalWidth>0)")
        pg.locator("#gallery").screenshot(path=str(SITE / f"preview-gallery-{name}.png"))
        print(name, "scrollWidth", pg.evaluate("document.documentElement.scrollWidth"))
    b.close()
