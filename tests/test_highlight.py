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
    await pg.click('button.lanehead[data-hl="freeride"]'); await pg.wait_for_timeout(700)
    print("lane hl:",await pg.evaluate("hl"),await pg.evaluate("document.querySelectorAll('.node.hl').length"))
    await pg.screenshot(path=f"{OUT}/H_freeride.png")
    await pg.click('button.lanehead[data-hl="freeride"]'); print("toggle off:",await pg.evaluate("hl"))
    # tiles show/hide a branch's skills on the main screen (not grey them out)
    await pg.evaluate("scrollTo(0,0)")
    for br in ["freeride","trunk"]:
      await pg.click(f'.prog[data-vis="{br}"]'); await pg.wait_for_timeout(200)
      print("tile hides",br,": cards left",await pg.evaluate(f"document.querySelectorAll('.node.b-{br}').length"),"tile off:",await pg.evaluate(f"document.querySelector('.prog[data-vis={br}]').classList.contains('off')"),"still in plan:",await pg.evaluate(f"shown({{branch:'{br}'}})"))
    await pg.screenshot(path=f"{OUT}/H_tiles_hidden.png")
    await pg.reload(); print("hidden persists:",await pg.evaluate("JSON.stringify(S.hidden)"))
    for br in ["freeride","trunk"]: await pg.click(f'.prog[data-vis="{br}"]')
    print("shown again: freeride",await pg.evaluate("document.querySelectorAll('.node.b-freeride').length"),"core",await pg.evaluate("document.querySelectorAll('.node.b-trunk').length"))
    await pg.click('button.lanehead[data-hl="trunk"] >> nth=0'); await pg.evaluate("window.scrollBy(0,0)")
    await pg.mouse.click(3,500); print("blank clears:",await pg.evaluate("hl"))
    await pg.evaluate("document.body.classList.add('sun')"); await pg.evaluate("drawLines()")
    await pg.screenshot(path=f"{OUT}/H_sun.png",full_page=True)
    print("small",await pg.evaluate("[...document.querySelectorAll('button')].filter(b=>b.offsetParent&&b.getBoundingClientRect().height<44).map(b=>b.textContent)"),"errs",errs)
    await b.close()
asyncio.run(main())
