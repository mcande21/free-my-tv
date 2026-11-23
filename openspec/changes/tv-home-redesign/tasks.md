**Goal:** the Front Range dusk look and the Horizon stage layout on the Free My TV home screen, installed on the
owner's TV from his fork.
**Gate:** `tools/check.sh web && tools/test-web.sh && tests/ui/run.sh` (run from the repo root; `tests/ui/run.sh`
needs Google Chrome and Python 3).
**Open Questions:** none.

## 1. Test harness and assets

- [x] 1.1 UI test harness: create `tests/ui/run.sh` (builds `python3 tizen/build.py --preview`, serves the repo root
      on 127.0.0.1:8766, runs Chrome `--headless=new --window-size=1920,1080 --virtual-time-budget=8000 --dump-dom`
      on `tests/ui/harness.html?case=<name>` for each case, fails on any `FAIL` line or a missing `PASS`),
      `tests/ui/harness.html` (seeds `fmtv.weather` from `tests/ui/weather-denver.json` and `fmtv.prefs`, loads
      `/out/tizen/index.html` in a same-origin 1920 x 1080 iframe, runs the case, writes `PASS <case>` or
      `FAIL <case>: <why>` into `#result`), `tests/ui/weather-denver.json` (a real Open-Meteo response shape for
      Denver, sunset 16:40, hourly 15:00-23:00, written by hand). First case `harness-loads`: asserts the iframe body
      has class `no-picks`. Run `tests/ui/run.sh`, expect PASS (it proves the harness, not a feature) · commit
      "test(ui): headless harness for the home screen"
- [x] 1.2 fonts: add `web/fonts/Outfit-300.woff2`, `Outfit-500.woff2`, `Geist-400.woff2`, `Geist-600.woff2` from
      `@fontsource/outfit@5.3.0` and `@fontsource/geist-sans@5.3.0` (latin subset) and `web/fonts/OFL-outfit-geist.txt`. Failing
      test first: case `fonts-loaded` asserts `document.fonts.check('300 96px Outfit')` and
      `document.fonts.check('400 32px Geist')` in the iframe; run, expect FAIL (no faces declared) · add the four
      `@font-face` rules to `web/home.css` above the Inter ones · gate, expect PASS · commit
      "feat(web): Outfit and Geist faces"
- [x] 1.3 icons, web only: add a `PHOSPHOR` map and a `--set phosphor` flag to `tools/make_symbols.py` (same app
      names as `MAP`, Phosphor regular names from `src/regular/selection.json`); render with Pillow in a throwaway
      venv into `web/symbols/` with `LICENSE-phosphor` (MIT); in `tools/webapp.py` `files()` copy `web/symbols/` after
      `app/assets/symbols/` so web names replace shared ones; also copy `OFL-outfit-geist.txt` from `web/fonts/`.
      Failing test first: case `icons-phosphor` asserts `out/tizen/symbols/settings.png` differs byte-for-byte from
      `app/assets/symbols/settings.png`, and `git diff --quiet app/assets/symbols` (Android untouched); run, expect
      FAIL (identical) · render and copy · gate, expect PASS · commit "feat(web): Phosphor icons for the web build"

## 2. Look

- [x] 2.1 palette and type: in `web/home.css` add the token key comment (design Decision 1), set `body` to
      `'Geist', 'Inter', 'LG Smart UI', 'Helvetica Neue', Arial, sans-serif` (line 29) and the same lead in
      `body.rtl` (line 671), night ground `#151A21`, ink `#ECE6DC`, muted `#97A0AC`, day ground `#E9E4DC`, day ink
      `#1C2128`; replace every `rgba(0, 0, 0,` shadow with `rgba(6, 10, 16,`; radii to 8/16/28. Failing test first:
      case `palette` asserts body computed `font-family` starts with `Geist`, no element under `#stage` has a computed
      color or background-color of the old Apple greys `rgb(29, 29, 31)`, `rgb(245, 245, 247)`, `rgb(110, 110, 115)`,
      and no element under `#home` has a box-shadow containing `rgba(0, 0, 0`; run, expect FAIL · change · gate,
      expect PASS · commit "feat(web): Front Range palette and type"
- [x] 2.2 accent focus: `.round.focus`, `.tab.focus` and the shelf's focused tile use the amber accent `#E3A15E`
      (3 px underline and `rgba(227, 161, 94, 0.35)` shadow) instead of a white fill. Failing test first: case
      `focus-accent` sends the shelf focus to tile 1 (dispatch `keydown` Right) and asserts the focused tile's
      underline colour is `rgb(227, 161, 94)`; run, expect FAIL · change · gate, expect PASS · commit
      "feat(web): amber focus"

## 3. Horizon stage layout

- [x] 3.1 safe margin and placement (spec: Safe margin): move `#clock` to top-left at (96, 54), `#buttons` to
      top-right ending at x 1824, the shelf (`#platter`, `#tiles`) to left-aligned at x 96 with its bottom at y 1026;
      remove the `#platter` glass gradient. Failing test first: case `safe-margin` asserts every box of `#clock`,
      `#weatherline`, `#buttons > *`, `#tiles > *` lies in x 96-1824, y 54-1026; run, expect FAIL (shelf starts at
      x 40) · change · gate, expect PASS · commit "feat(web): Horizon stage placement"
- [x] 3.2 weather line (spec: Clock and weather anchored top left): add `<div id="weatherline">` after `#clock` in
      `web/index.html`; in `web/home.js` render it beside `renderPanels` from `weatherParts(Data.weather)` plus the
      next three `hourly` readings after now; hide it when `!Prefs.weather()` or no weather. Failing tests first:
      cases `weather-line` (fixture at 14:20: expects text containing `15:00`, `16:00`, `17:00` with their fixture
      temperatures, in that order), `weather-none` (no `fmtv.weather`: `#weatherline` hidden, `#clock` box
      unchanged), `weather-off` (prefs weather false: hidden); run, expect FAIL · change · gate, expect PASS ·
      commit "feat(web): weather line under the clock"
- [x] 3.3 sun phase (spec: Horizon follows the sun): first confirm `grep -rnw Sun web` shows only the `'weekday|Sun'` string at data.js:29. Create
      `web/sun.js` (global `Sun`, ES5, `Sun.phase(nowMs, sunriseMs, sunsetMs)` per design Decision 4, falling back
      to clock hours when either time is missing, 0 or not a finite number) and `tests/WebSunTest.js` (vm sandbox like
      WebPrefsTest.js) added to `tools/test-web.sh`. Failing tests first, values derived by hand for sunrise 06:58,
      sunset 16:40: 17:00 -> `dusk`; 17:30 -> `night`; 06:30 -> `dawn`; 12:00 -> `day`; no times at 20:00 ->
      `night`, at 12:00 -> `day`; times 0, NaN or undefined at 12:00 -> `day`. Run, expect FAIL (no web/sun.js) · implement ·
      gate, expect PASS · commit "feat(web): sun phase"
- [x] ~~3.6 horizon canvas: three drawn ridges on a canvas~~ superseded by 3.7: ruling 2026-11-21 (photographs)
- [x] 3.4 shelf focus (spec: Shelf focus): tiles icon-only; the focused tile scales its icon to 1.15 and fades in
      its name; one tile width, no reflow. Failing test first: case `shelf-focus` moves focus 0 to 1 and asserts
      tile 1 has a visible name (opacity 1), tile 0's name opacity 0, and tile 2's left edge did not move; run,
      expect FAIL · change · gate, expect PASS · commit "feat(web): shelf focus grows the app"
- [x] 3.5 motion (design Decision 8): entrance stagger for `#clock`, `#weatherline`, `#tiles` (translateY 24 px and
      opacity, 420 ms, 80 ms apart), sky 2 s crossfade. Failing test first: case `motion-props` asserts the three
      elements' computed `transition-property` lists only `transform` and/or `opacity`; run, expect FAIL · change · gate, expect PASS · commit
      "feat(web): entrance and sky motion"

- [x] 3.7 photo backdrop (spec: Horizon follows the sun; Photo cannot load): crop the four photos (design
      Decision 3) to 1920 x 1080 JPEG q78 into `web/photos/{dawn,day,dusk,night}.jpg` with `web/photos/CREDITS.txt`
      (Decision 14); `tools/webapp.py` packs `web/photos/`; replace `<canvas id="horizon">` with `<img id="horizon"
      alt="">`; `updateHorizon` sets `src` to `photos/<phase>.jpg` and `data-phase`, and its `error` handler hides
      it; remove the canvas drawing code (HORIZON, RIDGES, drawHorizon). Failing tests first: UI case
      `backdrop-photo` (Denver fixture: `#horizon` is an image whose `src` ends in `photos/<data-phase>.jpg`, loaded,
      `naturalWidth` 1920) and `backdrop-fallback` (set `#horizon` `src` to a missing file: after the error it is not
      displayed and `#sky .grad` shows); `horizon-drawn` retires with the canvas. Run, expect FAIL · change · gate,
      expect PASS · commit "feat(web): Front Range photo backdrop"
- [x] 3.8 readable over the photo (spec: Text stays readable over the photo): add `<div id="scrim">` over the photo
      (top-left and bottom dark gradient, no-picks only) and, with a photo shown, the night ink for `#clock`,
      `#weatherline` and `.tile .label`. Failing check first: the measurement (design Decision 15) run from the
      mission's scratch on screenshots of all four phases, expect some text box under 3:1 before the scrim ·
      change · rerun, expect every box at or over 3:1 · gate, expect PASS · commit "feat(web): text stays readable
      over the photos"
- [x] 3.9 white logos (design Decision 16; spec: Shelf tiles share one surface): fetch the nine Simple Icons 16.38.0
      SVGs by `gh api repos/simple-icons/simple-icons/contents/icons/<name>.svg?ref=16.38.0`, set `fill="#FFFFFF"`
      and a width and height, into `web/icons/mono/`; make `mono/prime.png` from `icons/prime.png` (RGB to white,
      alpha kept) with a Pillow script kept in the mission scratch, not the repo; `web/icons/mono/CREDITS.txt`
      (source, tag, CC0). Add the mono path as a fifth SHELF column; confirm `tools/webapp.py` packs
      `web/icons/mono/` (add it if not). Failing test first: case `tiles-mono` (preview apps: the Netflix tile's img
      `src` ends `icons/mono/netflix.svg`; the Disney+ tile shows a visible word and no img); run, expect FAIL · change
      · gate, expect PASS · commit "feat(web): white logos for the shelf"
- [x] 3.10 one surface, six tiles, ring focus (Decisions 6 and 16; specs: Shelf focus, Shelf tiles share one
      surface): `SHELF_VISIBLE` 6, tile width at most 240; shelf tiles take the slate surface instead of `paint()`;
      `.tile.focus` scale 1.08 with `0 0 0 3px #E3A15E` and an amber glow; drop the underline and the icon-only
      scale. Failing tests first: new case `tiles-surface` (every visible tile has the same computed
      background-color; six tiles inside the safe area, each 240 px wide by `offsetWidth`); update `focus-accent`
      (ring colour `rgb(227, 161, 94)` in the focused tile's box-shadow) and `shelf-focus` (tile 1's computed
      transform scale 1.08, tile 0 back to 1, tile 2 `offsetLeft` unchanged); `safe-margin` must still pass with
      focus on tile 0; run, expect FAIL · change · gate, expect PASS, count cases defined vs ran · commit
      "feat(web): one surface for the shelf"
- [x] 3.11 type steps (Decision 17; spec: Type reads from the couch): add `web/fonts/Outfit-400.woff2`
      (`@fontsource/outfit@5.3.0`, latin) and its `@font-face`; `#clock` 160 px weight 400, `.date` 38 px, the weather
      line on two lines at 32 px, `.tile .label` 30 px. Failing tests first: `fonts-loaded` adds
      `document.fonts.check('400 160px Outfit')`; new case `type-scale` (computed sizes: clock 160 and weight 400,
      date 38, label 30; every text box under `#clock`, `#weatherline` and `.tile .label` at 29 px or more); run,
      expect FAIL · change · gate, expect PASS · rerun the readability measurement (Decision 15) on all four phases,
      expect every box at 3:1 or more · commit "feat(web): type steps for the couch"
- [x] 3.12 tile depth (Decision 18): failing test first: new case `tile-depth` (focus tile 1: its logo's computed
      transform moves it up 4 px and its filter has a drop-shadow; tile 1's box-shadow holds `rgba(6, 10, 16, 0.45)`;
      tile 0's logo is back at no lift; every tile's box-shadow holds the inset top highlight); run, expect FAIL ·
      change `web/home.css` only · gate, count cases defined vs ran; `motion-props` must still pass · rerun the
      readability measurement · screenshot at dusk for the owner · commit "feat(web): tile depth"

## 4. Must not change

- [x] 4.1 regressions (specs: Crypto prices off in this build; Way back unchanged): cases `crypto-off` (prefs and
      config with show_crypto false: `#quotes` empty or hidden) and `drawer-opens` (focus on shelf, dispatch
      `keydown` Down: body gains `drawer-open`). Run against the branch before group 2 lands to confirm they PASS
      on the old code too (behaviour kept), and keep them in the suite · commit "test(ui): crypto and drawer
      unchanged"

## 5. Ship to the TV

- [x] 5.1 owner build (reopened 2026-11-21: rebuild after 3.9-3.11): set `tizen/config.xml` `version="1.5.1"` (design Decision 13, committed "chore(tizen): 1.5.1 for the fork") and the owner's `config.properties` (design Decision 9), `python3 tizen/build.py`, expect
      `Built FreeMyTV-tizen.wgt`; before/after screenshots from `--preview` at 1920 x 1080 into the mission scratch
      folder; re-run the audit list and record which patterns are gone · no commit (config is git-ignored)
- [x] 5.2 fork and release (owner's yes first): `gh repo fork simbasjungles/free-my-tv --clone=false`, push branch
      `design/tv-home-redesign` to the fork, publish release `v1.5.1-frontrange` with `FreeMyTV-tizen.wgt`;
      verify with `gh release view -R mcande21/free-my-tv`
- [ ] 5.3 install: TizenBrew Installer, connect 192.168.0.21, install `mcande21/free-my-tv`; verify
      `GET http://192.168.0.21:8001/api/v2/applications/FreeMyTVio.FreeMyTV` shows `"version":"1.5.1"` and launches;
      the owner confirms the screen
- [ ] 5.4 Home button (ruling home-button; Decisions 9 and 13): `tizen/config.xml` `version="1.5.2"` (commit "chore(tizen):
      1.5.2 for the Home button") and `samsung_home_button=true` in the owner's `config.properties`; gate;
      `python3 tizen/build.py`, expect the With samsung_home_button line and the package's `config.xml` carrying
      `reload="disable"`; release `v1.5.2-frontrange` on the fork; install with TizenBrew Installer; verify the TV API
      shows `"version":"1.5.2"` and launches; the owner presses Home in another app and Free My TV comes back
