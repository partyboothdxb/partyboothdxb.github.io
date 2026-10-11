from playwright.sync_api import sync_playwright
import pathlib
url = pathlib.Path("/workspace/photobooth-site/index.html").as_uri()
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, w, h, dsf in [("desktop",1280,900,1),("mobile",390,844,2)]:
        pg = b.new_page(viewport={"width":w,"height":h}, device_scale_factor=dsf)
        errs=[]; pg.on("console", lambda m: errs.append(m.text) if m.type=="error" else None)
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(url, wait_until="networkidle")
        pg.evaluate("document.querySelectorAll('img').forEach(i=>i.loading='eager')")
        # preview only: hide sticky header + floating button so they don't cover the section
        pg.add_style_tag(content="header{position:static!important}.fab{display:none!important}")
        sec = pg.locator("#shop")
        sec.scroll_into_view_if_needed()
        pg.wait_for_function("[...document.querySelectorAll('#shop img')].every(i=>i.complete && i.naturalWidth>0)")
        pg.wait_for_timeout(800)
        info = pg.evaluate("""()=>({sw:document.documentElement.scrollWidth, cw:document.documentElement.clientWidth,
          cards:document.querySelectorAll('#shop .prop').length,
          rows:[...new Set([...document.querySelectorAll('#shop .prop')].map(e=>Math.round(e.getBoundingClientRect().top)))].length,
          btnH:[...document.querySelectorAll('#shop .prop .btn')].map(e=>Math.round(e.getBoundingClientRect().height)), btnOverflow:[...document.querySelectorAll('#shop .prop .btn')].some(e=>e.scrollWidth>e.clientWidth),
          href:document.querySelector('#shop .prop .btn').href,
          hrefLast:document.querySelectorAll('#shop .prop .btn')[5].href,
          booking:document.querySelector('.js-wa[data-pkg]').href})""")
        sec.screenshot(path=f"/workspace/photobooth-site/preview-shop-{name}.png")
        print(name, info, "errs", errs)
    # nav check at a narrow desktop width
    for W in (901,960,1024,1100):
      pg = b.new_page(viewport={"width":W,"height":600})
      pg.goto(url, wait_until="networkidle")
      print(W, pg.evaluate("({sw:document.documentElement.scrollWidth, navH:document.querySelector('.nav-links').getBoundingClientRect().height, btnH:document.querySelector('.nav .btn').getBoundingClientRect().height})"))
    print("nav920", pg.evaluate("({sw:document.documentElement.scrollWidth, navH:document.querySelector('.nav-links').getBoundingClientRect().height, links:[...document.querySelectorAll('.nav-links a')].map(a=>a.textContent)})"))
    pg.screenshot(path="/tmp/nav920.png", clip={"x":0,"y":0,"width":920,"height":90})
    b.close()
