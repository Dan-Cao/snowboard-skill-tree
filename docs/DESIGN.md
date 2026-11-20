# On Edge — design decisions

This records what Dan asked for, how "good" was defined, and why the app is built the way it is. Read it before changing content or UI. When a decision changes, update this file in the same commit.

## Who it's for

- **Dan**: an adult, **goofy** rider (right foot forward). He trained at The Snow Centre, Hemel Hempstead: passed level 5, did a level 5–6 day, and can ride a button lift in switch.
- **Starting point (Nov 2026):** linked skidded turns on blue are done; grippy turns are being learned.
- **Weak spots:** speed control on steeper pitches, and getting stuck on flats.
- **Trip:** Tignes / Val d'Isère (Espace Killy), 27 Dec 2026 – 10 Jan 2027, about 10 riding days. Mix of lesson days and solo days.
- **Trip goal:** comfortable on reds and first carves (skills marked ★).
- **Device:** Samsung Galaxy Z Fold. **Both the cover screen (~390 px) and the inner screen (~700 px) must work well.**

## Purpose

The main job is to **plan what to practise next**. Tracking progress comes second. Practise happens mostly abroad, with lesson-vs-solo mattering.

## Content rules

- **Teaching standard:** order and terminology follow how **BASI** (British Association of Snowsports Instructors) teaches: basic → skidded → carved/dynamic turns, with edge, pivot and pressure language (e.g. "progressive edging"). BASI's Central Theme manual isn't public, so reviews have checked against general BASI practice.
- **No Hemel level tags.** Skills used to carry a loose "≈ Hemel 6" / "Beyond Hemel" tag. Removed in Nov 2026 because Dan has worked through the Hemel levels, so they no longer help.
- **Every skill has:**
  - `pp` (optional): links to Progresspedia guides (progresspedia.org/courses/snowboarding/) as `[title, slug]`, shown under "Progresspedia guides" in the details sheet. Only link a page whose content really covers the skill; leave it out otherwise. The card notes that guides need signal and may describe a regular stance.
  - `desc`: one plain line (about 110 characters max) saying what the skill is. No left/right in it.
  - `test`: a measurable done-when test, using a rep count and/or a terrain grade or feature size (e.g. "10 linked turns on a red", "small kicker, table up to 4 m"). Avoid vague tests like "feels good" or "the steepest blue you know".
  - `drills`
  - `mistakes`
  - `tag`: `lesson` / `solo` / `either`
  - `area`: an **area-level** tip for Tignes / Val d'Isère. Don't name specific runs unless you've verified them against the current piste map.
  - `safety`: required for anything off-piste or in the park.
- **Goofy-specific directions:**
  - The right foot is front and the left foot is back.
  - Toeside turns go to the rider's **left** and heelside turns to the **right**.
  - In switch, the left shoulder leads.
  - Re-check every left/right/front/back reference when editing.
- **Off-piste safety is shown as notes, not as locks.** It must mention avalanche kit and training, a guide, the avalanche forecast, and insurance for off-piste rescue in France.
- **Not generic:** content should be tied to Dan's level, stance, weak spots (`weak: "speed" | "flats"`) and the trip.

## Structure

- **Core riding** (`trunk`) is always shown. It starts from the root skill T1 and splits into three lanes: **Turns**, **Speed control**, and **Terrain & switch**. Switch is folded into core riding rather than being its own branch.
- **Early core order follows Hemel's levels 1–5** (Nov 2026, Dan's call after comparing with Hemel and Progresspedia): hockey stops (T13) come straight after turn-shape speed control (T2) and before short turns (T7), because Hemel teaches stopping safely in stage 5 and Progresspedia builds short turns on hockey stops. Skating & one-foot (T5, a Hemel stage 1 skill) needs only T1 and comes before flat-base gliding (T4).
- **Optional branches** can be toggled in ☰ → Branches or with the ⚙ next to the legend:
  - Carving and Freeride: on by default, both go all the way to expert.
  - Ground tricks, Jumps, Rails & boxes, Halfpipe, Backcountry, Boardercross: off by default.
- Each branch in `BINFO` (app.html) has a short description and a level range (1 Beginner – 4 Expert). The chooser sorts branches from easiest to hardest to start.
- **Prerequisites are soft.** Everything can be ticked. A skill whose prerequisites are all done shows as "Next up".
- **Statuses:** locked / learning / done. When a skill moves from learning to done is **Dan's call**; the test is a guide. There's no XP or gamification ("keep it practical").
- Notes, date achieved and video links are logged per skill.

## Today's plan

- Choose a lesson day or a solo day, and the plan picks **2–3 skills max**.
- Solo days skip lesson-only skills. Lesson days lead with a lesson focus, then afternoon practice.
- Each pick gets a **short paragraph** on why it was chosen and how to spend the time, plus Dan's last note on that skill.
- Only today's plan is kept, and skills in hidden branches are left out.
- The plan doesn't adapt to snow or energy ("keep it simple").

## UI decisions

- **Look:** video-game styling (dark, glowing) but **readable in bright sun**.
- **Themes** (☰ → Theme, saved as `theme`): **Night** (default, dark glow), **Bluebird** (sky blue, white cards), **Bubblegum** (candy pink, extra-round), **Paper** (minimal warm off-white, red-orange accent), **Slate** (minimal cool grey, teal accent) and **Sun** (high contrast for bright days). Dan asked for fun options in Nov 2026. Every theme must keep Done/Learning/Next up/Locked clearly distinct. Old saves with `sun:true` load as the Sun theme.
- **Layout:** straight lanes plus **focus mode**.
  - The always-on lines only join adjacent skills within a lane.
  - Tapping a skill highlights what it needs (pink) and what it unlocks (blue), and opens a bottom bar with status buttons.
  - The bar also shows the skill's one-line `desc`, so Dan can tell at a glance what it is and whether he's done it. The same line sits at the top of the details sheet.
  - Tapping the same skill again opens its details. Tapping any blank area closes focus.
  - Dotted lines across the whole tree were rejected as unclear.
- **Branch identity:** each branch has a colour stripe on its cards and a tinted lane. Tapping a lane heading or a progress tile highlights that branch.
- **Tap targets are at least 44 px.** Cards use short names (`SHORT` in app.html) so three lanes fit on the cover screen.
- **Rarely used controls are kept small or in ☰.** For example, the branch chooser is a cog, and the branch on/off controls are switches without text.
- **Logging speed:** changing a status plus adding a note should take under 15 seconds.

## Data and offline

- The app is an **offline PWA on GitHub Pages**. It's installed to the home screen and opens from scratch with no signal.
- Hosted claude.ai artifacts were rejected because they don't allow service workers or downloads.
- Progress is stored in `localStorage` under key `sbtree.v1`, on each device only.
- **Never lose progress.** There's backup export (file download or copied text) and restore, and the app nudges for a backup after changes.
- `merge()` must keep old saved data loading, so new fields need defaults.
- Updating the app may require re-importing a backup; that's acceptable.
- **Dropbox sync** is a parked stretch goal. The plan was browser-only OAuth PKCE with an app-folder app and a per-skill merge.

## Verification process

These were agreed as acceptance checks:

1. **Before shipping content changes,** an independent review against BASI practice, checking goofy left/right, measurable tests, prerequisites and safety. Use a separate agent that didn't write the content.
2. **Phone-size tests** at 390 px and 700 px: no sideways overflow, no overlapping cards, tap targets at least 44 px, no JS errors. See `tests/`.
3. **Offline and backup:** the service worker serves the app with no network, and backup → wipe → restore round-trips.
