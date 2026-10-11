from playwright.sync_api import sync_playwright
url = "http://localhost:8765/index.html"
with sync_playwright() as p:
    b = p.chromium.launch()
    for name, w, h, dsf in [("desktop",1280,900,1),("mobile",390,844,2)]:
        pg = b.new_page(viewport={"width":w,"height":h}, device_scale_factor=dsf)
        errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.goto(url, wait_until="load")
        pg.add_style_tag(content="header{position:static!important}.fab{display:none!important}")
        sec = pg.locator("#calendar"); sec.scroll_into_view_if_needed()
        pg.wait_for_timeout(9000)
        fr = [f for f in pg.frames if "cal.com" in f.url]
        txt = fr[0].evaluate("document.body.innerText.slice(0,400)") if fr else None
        info = pg.evaluate("""()=>{const i=document.querySelector('#cal-inline iframe');return {sw:document.documentElement.scrollWidth,cw:document.documentElement.clientWidth,
          iframe:!!i, ifH:i&&Math.round(i.getBoundingClientRect().height), ifW:i&&Math.round(i.getBoundingClientRect().width), contH:Math.round(document.querySelector('#cal-inline').getBoundingClientRect().height),
          nav:[...document.querySelectorAll('.nav-links a')].map(a=>a.textContent), hero:document.querySelector('.hero .btn-ghost').outerHTML,
          wa:[...document.querySelectorAll('.cal-fallback .js-wa')].map(a=>a.href)}}""")
        sec.screenshot(path=f"/workspace/photobooth-site/preview-calendar-{name}.png")
        print(name, info, "\nframe:", [f.url[:160] for f in fr], "\ntext:", repr(txt), "\nerrs", errs)
    b.close()
