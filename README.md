# On Edge – Snowboard Skill Tree

Personal snowboarding progression tree (core riding, carving, freeride, plus optional trick, park, backcountry and boardercross branches) with drills, done-when tests, a session planner and on-device progress tracking. Installable offline PWA.

- Edit content in `skills.js`, UI in `app.html`, then run `python3 build.py` and bump `VERSION` in `sw.js`.
- Progress is stored in the browser on each device (localStorage). Use ☰ → Backup to export.
- Design decisions and acceptance checks: `docs/DESIGN.md`. Agent notes: `CLAUDE.md`.
- Tests: `sh tests/run_all.sh` (Playwright).
