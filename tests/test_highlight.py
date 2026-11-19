import pathlib
ROOT=pathlib.Path(__file__).resolve().parent.parent
URL=(ROOT/"index.html").as_uri()
OUT=str(ROOT/"tests"/"out"); pathlib.Path(OUT).mkdir(exist_ok=True)
import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await (await b.new_context(viewport={"width":390,"height":860},device_scale_factor=2)).new_page()
    errs=[]; pg.on("pageerror",lambda e:errs.append(str(e)))
    await pg.goto(URL); await pg.wait_for_timeout(300)
    await pg.screenshot(path=f"{OUT}/H_full.png",full_page=True)
    await pg.click('button.lanehead[data-hl="carving"]'); await pg.wait_for_timeout(700)
    print("hl:",await pg.evaluate("hl"),"lit:",await pg.evaluate("document.querySelectorAll('.node.hl').length"))
    await pg.screenshot(path=f"{OUT}/H_carving.png")
    await pg.mouse.click(195,30+400); await pg.wait_for_timeout(100)
    await pg.evaluate("scrollTo(0,0)"); await pg.click('.prog[data-hl="freeride"]'); await pg.wait_for_timeout(700)
    print("tile hl:",await pg.evaluate("hl"),await pg.evaluate("document.querySelectorAll('.node.hl').length"))
    await pg.screenshot(path=f"{OUT}/H_freeride.png")
    await pg.click('.prog[data-hl="freeride"]') if await pg.is_visible('.prog[data-hl="freeride"]') else await pg.click('button.lanehead[data-hl="freeride"]')
    print("toggle off:",await pg.evaluate("hl"))
    await pg.click('button.lanehead[data-hl="trunk"] >> nth=0'); await pg.evaluate("window.scrollBy(0,0)")
    await pg.mouse.click(3,500); print("blank clears:",await pg.evaluate("hl"))
    await pg.evaluate("document.body.classList.add('sun')"); await pg.evaluate("drawLines()")
    await pg.screenshot(path=f"{OUT}/H_sun.png",full_page=True)
    print("small",await pg.evaluate("[...document.querySelectorAll('button')].filter(b=>b.offsetParent&&b.getBoundingClientRect().height<44).map(b=>b.textContent)"),"errs",errs)
    await b.close()
asyncio.run(main())
