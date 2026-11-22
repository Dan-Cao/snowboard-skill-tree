# Dropbox automatic backup, against a fake Dropbox. The app is served at its real GitHub Pages URL through
# Playwright routing, with a test app key swapped in, so the OAuth redirect and secure context behave as live.
import pathlib, asyncio, json, sys, urllib.parse
from playwright.async_api import async_playwright
ROOT=pathlib.Path(__file__).resolve().parent.parent
OUT=str(ROOT/"tests"/"out"); pathlib.Path(OUT).mkdir(exist_ok=True)
APP="https://dan-cao.github.io/snowboard-skill-tree/"
HTML=(ROOT/"index.html").read_text().replace('const DBX_KEY="";','const DBX_KEY="testkey";')
assert 'DBX_KEY="testkey"' in HTML, "DBX_KEY constant not found"
CORS={"Access-Control-Allow-Origin":"*","Access-Control-Allow-Headers":"*","Access-Control-Allow-Methods":"POST, OPTIONS"}
fails=[]
def check(ok,msg):
  print(("PASS " if ok else "FAIL ")+msg)
  if not ok: fails.append(msg)

class FakeDropbox:
  def __init__(s): s.files={}; s.uploads=[]; s.down=False; s.expire_next=False; s.refreshes=0; s.auth=None; s.revoked=False
  async def route(s,r):
    q=r.request; u=q.url
    if q.method=="OPTIONS": return await r.fulfill(status=200,headers=CORS)
    if u.startswith("https://www.dropbox.com/oauth2/authorize"):
      s.auth=dict(urllib.parse.parse_qsl(urllib.parse.urlparse(u).query))
      # A script redirect, because Playwright doesn't route the follow-up request of a fulfilled 302
      back=s.auth["redirect_uri"]+"?code=C1&state="+s.auth["state"]
      return await r.fulfill(status=200,content_type="text/html",body="<script>location.replace(%s)</script>"%json.dumps(back))
    if s.down: return await r.abort()
    if u.endswith("/oauth2/token"):
      f=dict(urllib.parse.parse_qsl(q.post_data))
      if f["grant_type"]=="authorization_code":
        ok=f["code"]=="C1" and f["client_id"]=="testkey" and f["redirect_uri"]==APP and len(f["code_verifier"])>=43
        return await r.fulfill(status=200 if ok else 400,headers=CORS,json={"access_token":"acc-tok-1","expires_in":14400,"refresh_token":"ref-tok-1"} if ok else {"error":"invalid_grant"})
      s.refreshes+=1
      return await r.fulfill(status=200,headers=CORS,json={"access_token":"acc-tok-2","expires_in":14400})
    if u.endswith("/2/auth/token/revoke"): s.revoked=True; return await r.fulfill(status=200,headers=CORS,json={})
    arg=json.loads(q.headers.get("dropbox-api-arg","{}"))
    if s.expire_next: s.expire_next=False; return await r.fulfill(status=401,headers=CORS,json={"error":"expired_access_token"})
    if u.endswith("/2/files/upload"):
      s.files[arg["path"]]=q.post_data; s.uploads.append(arg["path"])
      return await r.fulfill(status=200,headers=CORS,json={"name":arg["path"]})
    if u.endswith("/2/files/download"):
      if arg["path"] not in s.files: return await r.fulfill(status=409,headers=CORS,json={"error_summary":"path/not_found/"})
      return await r.fulfill(status=200,headers=CORS,body=s.files[arg["path"]])
    return await r.fulfill(status=404,headers=CORS)

async def phone(b,dbx,w=390,h=860):
  ctx=await b.new_context(viewport={"width":w,"height":h},device_scale_factor=2,service_workers="block")
  await ctx.route(APP+"**",lambda r: r.fulfill(status=200,content_type="text/html",body=HTML) if urllib.parse.urlparse(r.request.url).path in ("/snowboard-skill-tree/","/snowboard-skill-tree/index.html") else r.fulfill(status=404))
  for host in ["https://www.dropbox.com/**","https://api.dropboxapi.com/**","https://content.dropboxapi.com/**"]: await ctx.route(host,dbx.route)
  pg=await ctx.new_page(); errs=[]
  pg.on("pageerror",lambda e:errs.append(str(e)))
  await pg.goto(APP); await pg.wait_for_timeout(200)
  return ctx,pg,errs

async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch()
    dbx=FakeDropbox()
    ctx,pg,errs=await phone(b,dbx)
    # 1. Connect on a phone with progress, empty Dropbox → uploads straight away
    await pg.click('[data-id="T3"]'); await pg.click('[data-id="T3"]'); await pg.click('#sheet .status [data-s="done"]'); await pg.click("#sheet [data-close]")
    await pg.click("#menuBtn"); await pg.locator("#dbxBox").screenshot(path=f"{OUT}/dropbox_connect.png")
    await pg.click("#dbxC"); await pg.wait_for_timeout(800)
    check(dbx.auth and dbx.auth["code_challenge_method"]=="S256" and dbx.auth["token_access_type"]=="offline" and dbx.auth["redirect_uri"]==APP,"authorize uses PKCE, offline token, redirect "+APP)
    check(pg.url==APP,"code removed from the address bar: "+pg.url)
    check(await pg.evaluate("document.getElementById('menuSheet').classList.contains('show')"),"menu opens after returning from Dropbox")
    check(sorted(dbx.uploads)==sorted(["/progress.json","/backups/"+await pg.evaluate("today()")+".json"]),"first upload writes progress.json and today's copy: "+str(dbx.uploads))
    up=json.loads(dbx.files["/progress.json"])
    check(up["data"]["status"]["T3"]=="done","uploaded data has the progress")
    check("tok-" not in dbx.files["/progress.json"],"tokens are not in the backup")
    check("Backed up automatically" in await pg.inner_text("#dbxBox"),"card says backed up")
    check(await pg.inner_text("#lastB")==await pg.evaluate("today()"),"Backup card shows today as last backup")
    await pg.locator("#dbxBox").screenshot(path=f"{OUT}/dropbox_connected.png")
    await pg.click("#menuSheet [data-close]")
    # 2. A change uploads a few seconds later; the daily copy is only written once a day
    n=len(dbx.uploads)
    await pg.click('[data-id="T13"]'); await pg.click('[data-id="T13"]'); await pg.click('#sheet .status [data-s="learning"]'); await pg.click("#sheet [data-close]")
    await pg.wait_for_timeout(1500); check(len(dbx.uploads)==n,"waits a few seconds before uploading")
    await pg.wait_for_timeout(3500)
    check(dbx.uploads[n:]==["/progress.json"] and json.loads(dbx.files["/progress.json"])["data"]["status"]["T13"]=="learning","change uploaded, no extra daily copy: "+str(dbx.uploads[n:]))
    check(await pg.evaluate("S.changes")==0 and not await pg.is_visible("#nudge"),"no backup nudge after upload")
    # 3. Expired access token → refreshed and retried
    dbx.expire_next=True; await pg.evaluate("S.theme='sun';save(false);dbxUpload()"); await pg.wait_for_timeout(500)
    check(dbx.refreshes==1 and json.loads(dbx.files["/progress.json"])["data"]["theme"]=="sun","401 refreshes the token and retries")
    # 4. No signal: changes wait, survive closing the app, and upload on next open
    dbx.down=True
    await pg.click('[data-id="T7"]'); await pg.click('[data-id="T7"]'); await pg.click('#sheet .status [data-s="learning"]'); await pg.click("#sheet [data-close]")
    await pg.wait_for_timeout(4500)
    check(await pg.evaluate("D.dirty"),"failed upload stays pending")
    await pg.click("#menuBtn"); check("Waiting for signal" in await pg.inner_text("#dbxBox"),"card says waiting for signal")
    await pg.locator("#dbxBox").screenshot(path=f"{OUT}/dropbox_waiting.png")
    dbx.down=False; await pg.reload(); await pg.wait_for_timeout(600)
    check(json.loads(dbx.files["/progress.json"])["data"]["status"]["T7"]=="learning","pending change uploads when the app opens again")
    # 5. New phone: Dropbox already has a backup → asks, uploads nothing, restores on request
    ctx2,pg2,errs2=await phone(b,dbx,700,840)
    n=len(dbx.uploads)
    await pg2.click("#menuBtn"); await pg2.click("#dbxC"); await pg2.wait_for_timeout(600)
    check(len(dbx.uploads)==n,"new phone does not overwrite the existing Dropbox backup")
    check("already has a backup" in await pg2.inner_text("#dbxBox"),"new phone asks what to do")
    await pg2.locator("#dbxBox").screenshot(path=f"{OUT}/dropbox_ask_inner.png")
    await pg2.click("#dbxAR"); await pg2.wait_for_timeout(5000)
    check(await pg2.evaluate("S.status.T3+','+S.status.T7")=="done,learning","restored the Dropbox backup onto the new phone")
    await pg2.reload(); await pg2.wait_for_timeout(300)
    check(await pg2.evaluate("S.status.T3")=="done" and await pg2.evaluate("!!D.refresh&&!D.ask"),"restore and connection persist after reload")
    # 6. Restore from Dropbox needs a confirm; Disconnect revokes and forgets the token
    await pg2.click("#menuBtn"); await pg2.click("#dbxR"); check(await pg2.is_visible("#dbxRY"),"restore asks to confirm")
    await pg2.click("#dbxD"); await pg2.wait_for_timeout(300)
    check(await pg2.evaluate("localStorage.getItem('sbtree.dbx')")=="{}" and await pg2.is_visible("#dbxC"),"disconnect forgets the token")
    # 7. Revoked access (invalid_grant) → asks to connect again
    await pg.evaluate("dbxAccess=null;D.refresh='BAD'")
    async def bad(r):
      if r.request.url.endswith("/oauth2/token"): return await r.fulfill(status=400,headers=CORS,json={"error":"invalid_grant"})
      await dbx.route(r)
    await ctx.route("https://api.dropboxapi.com/**",bad)
    await pg.click("#menuBtn"); await pg.evaluate("dbxQueue();dbxUpload()"); await pg.wait_for_timeout(500)
    await pg.locator("#dbxBox").screenshot(path=f"{OUT}/dropbox_lost.png")
    check("access was removed" in await pg.inner_text("#dbxBox"),"revoked access asks to connect again")
    # 8. Tap targets and overflow on both screens
    for g in (pg,pg2):
      small=await g.evaluate("[...document.querySelectorAll('#menu button')].filter(b=>b.offsetParent&&b.getBoundingClientRect().height<44).map(b=>b.textContent)")
      check(not small and not await g.evaluate("document.documentElement.scrollWidth>innerWidth"),"menu: no small buttons or overflow "+str(small))
    check(not errs and not errs2,"no JS errors "+str(errs+errs2))
    await b.close()
  if fails: print(len(fails),"failed"); sys.exit(1)
asyncio.run(main())
