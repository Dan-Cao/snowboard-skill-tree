import pathlib
ROOT=pathlib.Path(__file__).resolve().parent.parent
URL=(ROOT/"index.html").as_uri()
OUT=str(ROOT/"tests"/"out"); pathlib.Path(OUT).mkdir(exist_ok=True)
import asyncio
from playwright.async_api import async_playwright
# The back button (Android back gesture) should close the top layer, not leave the app.
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await (await b.new_context(viewport={"width":390,"height":860})).new_page()
    errs=[]; pg.on("pageerror",lambda e:errs.append(str(e)))
    await pg.goto(URL); await pg.wait_for_timeout(200)
    async def back(): await pg.go_back(); await pg.wait_for_timeout(150)
    shown=lambda i:pg.evaluate(f"document.getElementById('{i}').classList.contains('show')")
    state=lambda:pg.evaluate("JSON.stringify({focus,cur:typeof cur!=='undefined'?cur:null,d:history.state&&history.state.d,url:location.pathname.split('/').pop()})")
    # focus -> back clears focus, stays in the app
    await pg.click('[data-id="T2"]'); await back()
    print("focus then back:",await state())
    # focus -> details -> back to focus -> back to tree
    await pg.click('[data-id="T2"]'); await pg.click('[data-id="T2"]')
    print(" details open:",await shown("sheet"))
    await back(); print(" back from details: sheet",await shown("sheet"),await state())
    await back(); print(" back again:",await state())
    # details -> Needs skill -> back returns to the first skill
    await pg.evaluate("openSkill('T7')"); await pg.wait_for_timeout(100)
    await pg.click('#detail [data-go="T13"]'); await pg.wait_for_timeout(100)
    print("went to:",await pg.evaluate("cur")); await back()
    print(" back to previous skill:",await pg.evaluate("cur"),"sheet",await shown("sheet"))
    await back(); print(" back closes details:",await shown("sheet"),await state())
    # plan and menu sheets
    for btn,sh in [("#planBtn","planSheet"),("#menuBtn","menuSheet"),("#brEdit","brSheet")]:
      await pg.click(btn); await pg.wait_for_timeout(100); o=await shown(sh); await back()
      print(f" {sh}: open {o} -> after back {await shown(sh)}")
    # closing with the X removes the history entry again, so back isn't 'used up'
    await pg.click('[data-id="T2"]'); await pg.click('[data-id="T2"]'); await pg.click('#sheet [data-close]'); await pg.wait_for_timeout(150)
    await pg.click('#fx'); await pg.wait_for_timeout(150)
    print("after closing by X/tap:",await state())
    print("errs",errs)
    await b.close()
asyncio.run(main())
