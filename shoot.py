from playwright.sync_api import sync_playwright
import pathlib
url = pathlib.Path("/workspace/photobooth-site/index.html").as_uri()
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, w, h, full in [("desktop",1280,800,True),("mobile",390,844,True),("mobile-fold",390,844,False)]:
        pg = b.new_page(viewport={"width":w,"height":h}, device_scale_factor=1 if name=="desktop" else 2)
        errs=[]; pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
        pg.goto(url, wait_until="networkidle")
        pg.wait_for_timeout(500)
        sw = pg.evaluate("document.documentElement.scrollWidth")
        out = f"/workspace/photobooth-site/preview-{name}.png"
        pg.screenshot(path=out, full_page=full)
        print(name, "scrollWidth", sw, "errs", errs, pg.evaluate("document.querySelector('.js-wa[data-pkg]').href"))
    b.close()
