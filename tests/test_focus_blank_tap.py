import pathlib
ROOT=pathlib.Path(__file__).resolve().parent.parent
URL=(ROOT/"index.html").as_uri()
OUT=str(ROOT/"tests"/"out"); pathlib.Path(OUT).mkdir(exist_ok=True)
import asyncio
from playwright.async_api import async_playwright
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await (await b.new_context(viewport={"width":390,"height":860})).new_page()
    await pg.goto(URL)
    async def t(desc,x,y,pre=None):
      await pg.click('[data-id="T7"]'); 
      if pre: await pre()
      await pg.mouse.click(x,y); await pg.wait_for_timeout(100)
      print(desc,"→ focus cleared:",await pg.evaluate("focus===null"))
    await t("gap between cards",193,5000//10)
    await t("legend text",30,170)
    await t("side margin",3,600)
    async def scroll(): await pg.evaluate("scrollTo(0,document.body.scrollHeight)"); await pg.wait_for_timeout(100)
    await pg.click('[data-id="T7"]'); await scroll()
    r=await pg.evaluate("(()=>{const e=[...document.querySelectorAll('p.muted')].find(p=>p.textContent.includes('Goofy stance'));const r=e.getBoundingClientRect();return [r.left+20,r.top+r.height/2]})()")
    await pg.mouse.click(r[0],r[1]); await pg.wait_for_timeout(100)
    print("footer text → focus cleared:",await pg.evaluate("focus===null"))
    # bar and other node shouldn't clear
    await pg.click('[data-id="T7"]'); await pg.click('#fbar .k'); print("tap bar text keeps focus:",await pg.evaluate("focus"))
    await pg.click('[data-id="T2"]'); print("tap other skill switches focus:",await pg.evaluate("focus"))
    await b.close()
asyncio.run(main())
