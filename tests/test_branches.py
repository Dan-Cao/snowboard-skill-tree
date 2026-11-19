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
      ctx=await b.new_context(viewport={"width":w,"height":h},device_scale_factor=2); pg=await ctx.new_page()
      errs=[]; pg.on("pageerror",lambda e:errs.append(str(e)))
      # simulate an existing user's saved state from before this update (no branches key)
      await pg.goto(URL)
      await pg.evaluate("localStorage.setItem('sbtree.v1',JSON.stringify({v:1,status:{T1:'done',T3:'done',T2:'learning'},notes:{T2:[{d:'2026-11-18',t:'old note'}]}}))"); await pg.reload()
      print(name,"old state ok:",await pg.evaluate("S.status.T3+' '+JSON.stringify(S.branches)"),"nodes",await pg.evaluate("document.querySelectorAll('.node').length"))
      await pg.click("#brEdit"); await pg.click('[data-b="ground"]'); await pg.click('[data-b="jumps"]'); await pg.click('[data-b="rails"]'); await pg.click('[data-b="freeride"]')
      await pg.screenshot(path=f"{OUT}/B_{name}_sheet.png")
      await pg.click("#brSheet [data-close]")
      print(" after toggles:",await pg.evaluate("JSON.stringify(S.branches)"),"nodes",await pg.evaluate("document.querySelectorAll('.node').length"),
        "overflow",await pg.evaluate("document.documentElement.scrollWidth>innerWidth"),
        "overlap",await pg.evaluate("""(()=>{const r=[...document.querySelectorAll('.node,.lanehead')].map(e=>e.getBoundingClientRect());let n=0;for(let i=0;i<r.length;i++)for(let j=i+1;j<r.length;j++){const a=r[i],b=r[j];if(a.left<b.right-1&&b.left<a.right-1&&a.top<b.bottom-1&&b.top<a.bottom-1)n++}return n})()"""),
        "small",await pg.evaluate("[...document.querySelectorAll('button')].filter(b=>b.offsetParent&&b.getBoundingClientRect().height<44).length"))
      await pg.screenshot(path=f"{OUT}/B_{name}_full.png",full_page=True)
      await pg.reload(); print(" persists:",await pg.evaluate("JSON.stringify(S.branches)"))
      await pg.click('[data-id="J1"]'); print(" focus J1 bar:",await pg.text_content("#fbar .k"))
      await pg.click("#fbar #fx")
      await pg.click("#planBtn"); await pg.click('[data-t="solo"]'); print(" plan:",await pg.evaluate("S.plan.items.map(i=>i.id)"),"hidden in plan:",await pg.evaluate("S.plan.items.some(i=>!shown(byId[i.id]))"))
      await pg.click("#planSheet [data-close]")
      await pg.click('button.lanehead[data-hl="jumps"]'); await pg.wait_for_timeout(500); print(" hl jumps lit:",await pg.evaluate("document.querySelectorAll('.node.hl').length"))
      print(" errs",errs); await ctx.close()
    await b.close()
asyncio.run(main())
