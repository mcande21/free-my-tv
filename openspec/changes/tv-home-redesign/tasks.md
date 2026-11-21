**Goal:** the Front Range dusk look and the Horizon stage layout on the Free My TV home screen, installed on the
owner's TV from his fork.
**Gate:** `tools/check.sh web && tools/test-web.sh && tests/ui/run.sh` (run from the repo root; `tests/ui/run.sh`
needs Google Chrome and Python 3).
**Open Questions:** none.

## 1. Test harness and assets

- [ ] 1.1 UI test harness: create `tests/ui/run.sh` (builds `python3 tizen/build.py --preview`, serves the repo root
      on 127.0.0.1:8766, runs Chrome `--headless=new --window-size=1920,1080 --virtual-time-budget=8000 --dump-dom`
      on `tests/ui/harness.html?case=<name>` for each case, fails on any `FAIL` line or a missing `PASS`),
      `tests/ui/harness.html` (seeds `fmtv.weather` from `tests/ui/weather-denver.json` and `fmtv.prefs`, loads
      `/out/tizen/index.html` in a same-origin 1920 x 1080 iframe, runs the case, writes `PASS <case>` or
      `FAIL <case>: <why>` into `#result`), `tests/ui/weather-denver.json` (a real Open-Meteo response shape for
      Denver, sunset 16:40, hourly 15:00-23:00, written by hand). First case `harness-loads`: asserts the iframe body
      has class `no-picks`. Run `tests/ui/run.sh`, expect PASS (it proves the harness, not a feature) · commit
      "test(ui): headless harness for the home screen"
- [ ] 1.2 fonts: add `web/fonts/Outfit-300.woff2`, `Outfit-500.woff2`, `Geist-400.woff2`, `Geist-600.woff2` from
      `@fontsource/outfit@5.3.0` and `@fontsource/geist-sans@5.3.0` (latin subset) and `web/fonts/OFL-outfit-geist.txt`. Failing
      test first: case `fonts-loaded` asserts `document.fonts.check('300 96px Outfit')` and
      `document.fonts.check('400 32px Geist')` in the iframe; run, expect FAIL (no faces declared) · add the four
      `@font-face` rules to `web/home.css` above the Inter ones · gate, expect PASS · commit
      "feat(web): Outfit and Geist faces"
- [ ] 1.3 icons, web only: add a `PHOSPHOR` map and a `--set phosphor` flag to `tools/make_symbols.py` (same app
      names as `MAP`, Phosphor regular names from `src/regular/selection.json`); render with Pillow in a throwaway
      venv into `web/symbols/` with `LICENSE-phosphor` (MIT); in `tools/webapp.py` `files()` copy `web/symbols/` after
      `app/assets/symbols/` so web names replace shared ones; also copy `OFL-outfit-geist.txt` from `web/fonts/`.
      Failing test first: case `icons-phosphor` asserts `out/tizen/symbols/settings.png` differs byte-for-byte from
      `app/assets/symbols/settings.png`, and `git diff --quiet app/assets/symbols` (Android untouched); run, expect
      FAIL (identical) · render and copy · gate, expect PASS · commit "feat(web): Phosphor icons for the web build"

## 2. Look

- [ ] 2.1 palette and type: in `web/home.css` add the token key comment (design Decision 1), set `body` to
      `'Geist', 'Inter', 'LG Smart UI', 'Helvetica Neue', Arial, sans-serif` (line 29) and the same lead in
      `body.rtl` (line 671), night ground `#151A21`, ink `#ECE6DC`, muted `#97A0AC`, day ground `#E9E4DC`, day ink
      `#1C2128`; replace every `rgba(0, 0, 0,` shadow with `rgba(6, 10, 16,`; radii to 8/16/28. Failing test first:
      case `palette` asserts body computed `font-family` starts with `Geist`, no element under `#stage` has a computed
      color or background-color of the old Apple greys `rgb(29, 29, 31)`, `rgb(245, 245, 247)`, `rgb(110, 110, 115)`,
      and no element under `#home` has a box-shadow containing `rgba(0, 0, 0`; run, expect FAIL · change · gate,
      expect PASS · commit "feat(web): Front Range palette and type"
- [ ] 2.2 accent focus: `.round.focus`, `.tab.focus` and the shelf's focused tile use the amber accent `#E3A15E`
      (3 px underline and `rgba(227, 161, 94, 0.35)` shadow) instead of a white fill. Failing test first: case
      `focus-accent` sends the shelf focus to tile 1 (dispatch `keydown` Right) and asserts the focused tile's
      underline colour is `rgb(227, 161, 94)`; run, expect FAIL · change · gate, expect PASS · commit
      "feat(web): amber focus"

## 3. Horizon stage layout

- [ ] 3.1 safe margin and placement (spec: Safe margin): move `#clock` to top-left at (96, 54), `#buttons` to
      top-right ending at x 1824, the shelf (`#platter`, `#tiles`) to left-aligned at x 96 with its bottom at y 1026;
      remove the `#platter` glass gradient. Failing test first: case `safe-margin` asserts every box of `#clock`,
      `#weatherline`, `#buttons > *`, `#tiles > *` lies in x 96-1824, y 54-1026; run, expect FAIL (shelf starts at
      x 40) · change · gate, expect PASS · commit "feat(web): Horizon stage placement"
- [ ] 3.2 weather line (spec: Clock and weather anchored top left): add `<div id="weatherline">` after `#clock` in
      `web/index.html`; in `web/home.js` render it beside `renderPanels` from `weatherParts(Data.weather)` plus the
      next three `hourly` readings after now; hide it when `!Prefs.weather()` or no weather. Failing tests first:
      cases `weather-line` (fixture at 14:20: expects text containing `15:00`, `16:00`, `17:00` with their fixture
      temperatures, in that order), `weather-none` (no `fmtv.weather`: `#weatherline` hidden, `#clock` box
      unchanged), `weather-off` (prefs weather false: hidden); run, expect FAIL · change · gate, expect PASS ·
      commit "feat(web): weather line under the clock"
- [ ] 3.3 sun phase (spec: Horizon follows the sun): first confirm `grep -rnw Sun web` shows only the `'weekday|Sun'` string at data.js:29. Create
      `web/sun.js` (global `Sun`, ES5, `Sun.phase(nowMs, sunriseIso, sunsetIso)` per design Decision 4, falling back
      to clock hours when either ISO string is missing or unparsable) and `tests/WebSunTest.js` (vm sandbox like
      WebPrefsTest.js) added to `tools/test-web.sh`. Failing tests first, values derived by hand for sunrise 06:58,
      sunset 16:40: 17:00 -> `dusk`; 17:30 -> `night`; 06:30 -> `dawn`; 12:00 -> `day`; no times at 20:00 ->
      `night`, at 12:00 -> `day`; garbage strings at 12:00 -> `day`. Run, expect FAIL (no web/sun.js) · implement ·
      gate, expect PASS · commit "feat(web): sun phase"
- [ ] 3.6 horizon canvas (spec: Horizon follows the sun): add `<canvas id="horizon" width="960" height="540">` in
      `#sky` and `<script src="sun.js">` before `home.js` in `web/index.html`; in `home.js` `drawHorizon(phase)` draws
      three ridges from a fixed seed and the phase sky, sets `data-phase` on the canvas, redraws only when
      `Sun.phase` changes in the minute tick, and skips drawing when `getContext('2d')` is null. Failing test first:
      UI case `horizon-drawn` asserts `#horizon` has a `data-phase` in {night, dawn, day, dusk} and a non-blank
      pixel at (480, 500); run, expect FAIL · change · gate, expect PASS · commit "feat(web): horizon canvas"
- [ ] 3.4 shelf focus (spec: Shelf focus): tiles icon-only; the focused tile scales its icon to 1.15 and fades in
      its name; one tile width, no reflow. Failing test first: case `shelf-focus` moves focus 0 to 1 and asserts
      tile 1 has a visible name (opacity 1), tile 0's name opacity 0, and tile 2's left edge did not move; run,
      expect FAIL · change · gate, expect PASS · commit "feat(web): shelf focus grows the app"
- [ ] 3.5 motion (design Decision 8): entrance stagger for `#clock`, `#weatherline`, `#tiles` (translateY 24 px and
      opacity, 420 ms, 80 ms apart), sky 2 s crossfade. Failing test first: case `motion-props` asserts the three
      elements' computed `transition-property` lists only `transform` and/or `opacity`; run, expect FAIL · change · gate, expect PASS · commit
      "feat(web): entrance and sky motion"

## 4. Must not change

- [ ] 4.1 regressions (specs: Crypto prices off in this build; Way back unchanged): cases `crypto-off` (prefs and
      config with show_crypto false: `#quotes` empty or hidden) and `drawer-opens` (focus on shelf, dispatch
      `keydown` Down: body gains `drawer-open`). Run against the branch before group 2 lands to confirm they PASS
      on the old code too (behaviour kept), and keep them in the suite · commit "test(ui): crypto and drawer
      unchanged"

## 5. Ship to the TV

- [ ] 5.1 owner build: set `tizen/config.xml` `version="1.5.1"` (design Decision 13, committed "chore(tizen): 1.5.1 for the fork") and the owner's `config.properties` (design Decision 9), `python3 tizen/build.py`, expect
      `Built FreeMyTV-tizen.wgt`; before/after screenshots from `--preview` at 1920 x 1080 into the mission scratch
      folder; re-run the audit list and record which patterns are gone · no commit (config is git-ignored)
- [ ] 5.2 fork and release (owner's yes first): `gh repo fork simbasjungles/free-my-tv --clone=false`, push branch
      `design/tv-home-redesign` to the fork, publish release `v1.5.1-frontrange` with `FreeMyTV-tizen.wgt`;
      verify with `gh release view -R mcande21/free-my-tv`
- [ ] 5.3 install: TizenBrew Installer, connect 192.168.0.21, install `mcande21/free-my-tv`; verify
      `GET http://192.168.0.21:8001/api/v2/applications/FreeMyTVio.FreeMyTV` shows `"version":"1.5.1"` and launches;
      the owner confirms the screen
