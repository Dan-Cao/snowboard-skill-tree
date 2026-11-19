# On Edge — agent notes

Personal snowboard skill tree PWA for Dan (goofy, intermediate). It's live at dan-cao.github.io/snowboard-skill-tree, served by GitHub Pages from `main` / root.

**Read `docs/DESIGN.md` before making changes.** It records the agreed requirements, the BASI-based content rules, the UI decisions and the acceptance checks.

## Files
- `skills.js`: all skill content (the `SKILLS` array). Edit content here.
- `app.html`: UI, styles and logic. It has a `/*__SKILLS__*/` placeholder.
- `index.html`: **generated** by `python3 build.py`, which inlines skills.js into app.html. Never edit it by hand.
- `sw.js`: service worker for offline use.
- `manifest.webmanifest`, `icon-*.png`: PWA install.
- `tests/`: Playwright browser tests (`sh tests/run_all.sh`).

## Every change
1. Edit `skills.js` and/or `app.html`.
2. Run `python3 build.py`.
3. **Bump `VERSION` in `sw.js`**, otherwise installed phones keep the old cache.
4. Run `sh tests/run_all.sh`. It needs `pip install playwright && python3 -m playwright install chromium`. Look at the screenshots in `tests/out/` at both 390 px and 700 px.
5. For content changes, get an independent review: goofy left/right, BASI order and terms, measurable tests, safety.
6. Commit `index.html` and `sw.js` along with your source changes.

## Don'ts
- Don't break loading of existing saved progress (`localStorage` key `sbtree.v1`). Add defaults in `fresh()`/`merge()`.
- Don't load anything from a CDN; the app must work fully offline.
- Don't name specific runs in `area` tips unless you've checked them against the current piste map.
