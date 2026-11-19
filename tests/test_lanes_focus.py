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
      ctx=await b.new_context(viewport={"width":w,"height":h},device_scale_factor=2)
      pg=await ctx.new_page(); errs=[]; pg.on("pageerror",lambda e:errs.append(str(e)))
      await pg.goto(URL); await pg.wait_for_timeout(400)
      print(name,"overflow",await pg.evaluate("document.documentElement.scrollWidth>innerWidth"),
        "nodes",await pg.evaluate("document.querySelectorAll('.node').length"),
        "small",await pg.evaluate("[...document.querySelectorAll('button')].filter(b=>b.offsetParent&&b.getBoundingClientRect().height<44).length"),
        "overlap",await pg.evaluate("""(()=>{const r=[...document.querySelectorAll('.node')].map(e=>e.getBoundingClientRect());let n=0;for(let i=0;i<r.length;i++)for(let j=i+1;j<r.length;j++){const a=r[i],b=r[j];if(a.left<b.right&&b.left<a.right&&a.top<b.bottom&&b.top<a.bottom)n++}return n})()"""))
      await pg.screenshot(path=f"{OUT}/L_{name}_full.png",full_page=True)
      await pg.click('[data-id="T11"]'); await pg.wait_for_timeout(200)
      await pg.evaluate("document.querySelector('[data-id=T11]').scrollIntoView({block:'center'})"); await pg.wait_for_timeout(150)
      await pg.screenshot(path=f"{OUT}/L_{name}_focus.png")
      await pg.click('#fbar [data-s="learning"]'); print(" status via bar:",await pg.evaluate("S.status.T11"))
      await pg.click('[data-id="T11"]'); print(" second tap opens sheet:",await pg.evaluate("document.getElementById('sheet').classList.contains('show')"))
      print(" errs",errs); await ctx.close()
    await b.close()
asyncio.run(main())
