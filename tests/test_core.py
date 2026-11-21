import pathlib
ROOT=pathlib.Path(__file__).resolve().parent.parent
URL=(ROOT/"index.html").as_uri()
OUT=str(ROOT/"tests"/"out"); pathlib.Path(OUT).mkdir(exist_ok=True)
import asyncio, json, sys
from playwright.async_api import async_playwright
URL=URL
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch()
    for name,w,h in [("cover",390,860),("inner",700,840)]:
      ctx=await b.new_context(viewport={"width":w,"height":h},device_scale_factor=2,offline=True,accept_downloads=True)
      pg=await ctx.new_page(); errs=[]
      pg.on("pageerror",lambda e:errs.append(str(e))); pg.on("console",lambda m: m.type=="error" and errs.append(m.text))
      await pg.goto(URL); await pg.wait_for_timeout(300)
      ow=await pg.evaluate("document.documentElement.scrollWidth>innerWidth")
      small=await pg.evaluate("[...document.querySelectorAll('button')].filter(b=>b.offsetParent&&(b.getBoundingClientRect().height<44)).map(b=>b.textContent.trim().slice(0,20))")
      await pg.screenshot(path=f"{OUT}/{name}_top.png")
      await pg.screenshot(path=f"{OUT}/{name}_full.png",full_page=True)
      print(name,"overflow",ow,"small",small,"errs",errs)
      if name=="cover":
        import time; t=time.time()
        await pg.click('[data-id="T3"]'); await pg.click('[data-id="T3"]'); await pg.fill("#noteIn","Weight forward on heelside"); await pg.click('#sheet .status [data-s="done"]')
        print("status+note secs (automation)",round(time.time()-t,2), await pg.text_content("#savedMsg"))
        await pg.screenshot(path=f"{OUT}/cover_detail.png")
        await pg.click("#sheet [data-close]")
        await pg.click("#planBtn"); await pg.click('[data-t="solo"]'); await pg.screenshot(path=f"{OUT}/cover_plan_solo.png",full_page=False)
        print("solo plan:",await pg.evaluate("S.plan.items.map(i=>i.id+':'+byId[i.id].tag)"))
        await pg.click('[data-t="lesson"]'); await pg.screenshot(path=f"{OUT}/cover_plan_lesson.png")
        print("lesson: picks",await pg.evaluate("S.plan.items.length"),"brief:",await pg.evaluate("document.querySelector('.brief').innerText.split('\\n').length"),"lines")
        await pg.select_option("#hwSkill","T13"); await pg.fill("#hwIn","Hockey stops on toeside, within 3 board lengths"); await pg.click("#hwSave")
        print(" homework saved:",await pg.evaluate("JSON.stringify(S.notes.T13.slice(-1)[0])"),await pg.text_content("#plan .saved"))
        await pg.click('[data-t="buddy"]'); await pg.screenshot(path=f"{OUT}/cover_plan_buddy.png",full_page=False)
        print("buddy plan:",await pg.evaluate("S.plan.items.map(i=>i.id)"),"homework card:",await pg.evaluate("document.querySelector('.pitem.hw').innerText.includes('Hockey stops on toeside')"),"no Sophie-level assumption:",await pg.evaluate("!document.querySelector('#plan').innerText.includes('stretch')"))
        await pg.click('[data-t="solo"]'); print(" solo with homework:",await pg.evaluate("S.plan.items.map(i=>i.id)"))
        await pg.click("#planSheet [data-close]")
        # persistence
        await pg.reload(); print("persist T3:",await pg.evaluate("S.status.T3"), await pg.evaluate("S.notes.T3"))
        # export
        await pg.click("#menuBtn")
        async with pg.expect_download() as d: await pg.click("#expB")
        dl=await d.value; path=f"{OUT}/backup.json"; await dl.save_as(path)
        # wipe & restore
        await pg.evaluate("localStorage.clear()"); await pg.reload()
        print("after wipe T3:",await pg.evaluate("S.status.T3"))
        await pg.click("#menuBtn"); await pg.set_input_files("#fileIn",path); await pg.wait_for_timeout(300)
        print("after restore T3:",await pg.evaluate("S.status.T3"),await pg.text_content("#menuMsg"))
        await pg.click("#menuSheet [data-close]")
        for th in ["sun","bluebird","bubblegum","paper","slate"]:
            await pg.click("#menuBtn"); await pg.click(f"[data-theme={th}]"); await pg.click("#menuSheet [data-close]"); await pg.screenshot(path=f"{OUT}/cover_{th}.png")
        await pg.reload(); print("theme persists:",await pg.evaluate("S.theme"),await pg.evaluate("document.body.className"))
        await pg.evaluate("localStorage.setItem('sbtree.v1',JSON.stringify(Object.assign(JSON.parse(localStorage.getItem('sbtree.v1')),{sun:true,theme:undefined})))"); await pg.reload(); print("old sun save ->",await pg.evaluate("S.theme"))
        # Foundations: a normal branch, off by default, all done, toggled in the branch chooser
        print("found statuses:",await pg.evaluate("['S1','S2','S3','S4','S5'].map(i=>st(i)).join(',')"),"T1 needs:",await pg.evaluate("byId.T1.pre.join(',')"),"cards:",await pg.evaluate("document.querySelectorAll('.node.b-found').length"))
        await pg.click("#brEdit"); await pg.click('[data-b="found"]'); await pg.click("#brSheet [data-close]")
        first=await pg.evaluate("document.querySelector('.lanes .node').dataset.id"); await pg.reload()
        print("found on: cards",await pg.evaluate("document.querySelectorAll('.node.b-found').length"),"first card:",first,"tile:",await pg.evaluate("!!document.querySelector('.prog.b-found')"),"persists:",await pg.evaluate("S.branches.found"))
        await pg.evaluate("localStorage.setItem('sbtree.v1',JSON.stringify(Object.assign(JSON.parse(localStorage.getItem('sbtree.v1')),{foundOpen:true,branches:{carving:true,freeride:true}})))"); await pg.reload()
        print("old foundOpen save -> found on:",await pg.evaluate("S.branches.found"),"foundOpen gone:",await pg.evaluate("!('foundOpen' in S)"))
        print("errs",errs)
      await ctx.close()
    await b.close()
asyncio.run(main())
