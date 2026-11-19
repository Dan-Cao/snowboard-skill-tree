import pathlib
ROOT=pathlib.Path(__file__).resolve().parent.parent
URL=(ROOT/"index.html").as_uri()
OUT=str(ROOT/"tests"/"out"); pathlib.Path(OUT).mkdir(exist_ok=True)
import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch()
    for name,w,h in [("cover",390,860),("inner",700,840)]:
      pg=await (await b.new_context(viewport={"width":w,"height":h},device_scale_factor=2)).new_page(); errs=[]; pg.on("pageerror",lambda e:errs.append(str(e)))
      await pg.goto(URL)
      r=await pg.evaluate("(()=>{const r=document.getElementById('brEdit').getBoundingClientRect();return [r.width,r.height]})()")
      await pg.screenshot(path=f"{OUT}/C_{name}_top.png",clip={"x":0,"y":0,"width":w,"height":420})
      await pg.click("#brEdit"); await pg.click('[data-b="ground"]')
      print(name,"cog size",r,"ground on:",await pg.evaluate("S.branches.ground"),"aria:",await pg.get_attribute('[data-b="ground"]',"aria-checked"),"errs",errs)
      await pg.screenshot(path=f"{OUT}/C_{name}_sheet.png")
      await pg.click("#brSheet [data-close]"); await pg.click("#menuBtn"); await pg.click("#brM"); print(" via menu:",await pg.evaluate("document.getElementById('brSheet').classList.contains('show')"))
    await b.close()
asyncio.run(main())
