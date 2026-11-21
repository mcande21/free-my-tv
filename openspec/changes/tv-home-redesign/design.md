## Context

`web/` is one page drawn at a fixed 1920 x 1080 stage (`#stage`, `.layer`), ES5 JavaScript in IIFEs (`TV`, `Data`,
`Prefs` are globals; `home.js` exports nothing). `tools/check.sh web` forbids CSS custom properties, grid and
backdrop-filter. Weather comes from Open-Meteo (48 hourly readings, today's sunrise and sunset) and is cached in
localStorage under `fmtv.weather`; preferences under `fmtv.prefs`. Icons are white PNGs rendered from a font by
`tools/make_symbols.py`. The owner runs without a TMDB key, so the page is in its `no-picks` state.

## Goals / Non-Goals

**Goals:** the Front Range dusk look and the Horizon stage layout in the no-picks state; type and colour carried to
the other surfaces; a UI test that drives the real page.

**Non-Goals:** new data sources; changes to the picks layout's structure; the Android app.

## Decisions

1. **Palette as literal values with a key at the top of `home.css`.** Custom properties are banned by the gate, so the
   tokens live in a comment block and are used literally: ground `#151A21`, slate `#1E2631`, ridge-far `#2A3442`,
   ridge-near `#10141A`, ink `#ECE6DC`, muted `#97A0AC`, accent amber `#E3A15E` (saturation under 80%), day ground
   `#E9E4DC`, day ink `#1C2128`. Shadows `rgba(6, 10, 16, a)`. Radii 8 / 16 / 28. Rejected: a preprocessor (adds a
   build step the repo does not have).
2. **Type: Outfit + Geist, local woff2, two weights each.** Outfit 300 and 500 for the time and headings; Geist 400
   and 600 for interface text; `font-variant-numeric: tabular-nums` on the time and temperatures. Files from
   `@fontsource/outfit` 5.3.0 and `@fontsource/geist-sans` 5.3.0 (OFL-1.1), latin subset, with `OFL.txt` beside them.
   Inter stays in the stack after Geist (home.css:29 and :671) and its files stay, for Cyrillic, Greek and Vietnamese glyphs the latin subsets lack. Rejected: Inter as the face (the audit's first finding); deleting Inter (other languages would fall to system fonts); a CDN (the app runs offline and from file://).
3. **Horizon on one canvas, redrawn only on phase change.** A new `<canvas id="horizon">` in `#sky`, 960 x 540 scaled
   to the stage, draws three ridge silhouettes from a fixed seeded profile and a vertical sky gradient for the phase.
   It redraws when the phase changes (checked each minute with the clock tick), never per frame. Rejected: CSS
   gradients plus SVG (no filter control on older TVs, larger markup); an image (a fixed look that cannot follow
   the sun).
4. **Sun phase** from cached `daily.sunrise[0]` and `daily.sunset[0]`: dawn = sunrise - 45 min to sunrise + 30 min;
   dusk = sunset - 30 min to sunset + 45 min; day between; night otherwise. No weather: night 19:00-07:00, else day.
5. **Weather line** reuses `weatherParts()` for the current reading and adds three hourly labels from
   `hourly.time`/`hourly.temperature_2m` after the current hour. Hidden when `Prefs.weather()` is false or no weather.
6. **Shelf focus** widens the tile with `transform: scale` on the icon and a name label that fades in (opacity only);
   the tile's box keeps one width so the row does not reflow. The accent is a 3 px amber underline plus an amber
   tinted shadow.
7. **Icons, web only:** the PNGs in `app/assets/symbols/` are shared with the Android app, so they stay. Phosphor
   renders into a new `web/symbols/` folder, and `tools/webapp.py` `files()` copies it after `app/assets/symbols/`,
   so a web name replaces the shared one in the LG and Samsung packages only. `tools/make_symbols.py` gains a Phosphor
   map (same app names, Phosphor regular glyph names) rendered from `Phosphor.ttf` of `@phosphor-icons/web` 2.1.2
   (MIT), `LICENSE-phosphor` beside them. Pillow runs from a throwaway virtualenv; a tool dependency only. Rejected:
   overwriting `app/assets/symbols/` (changes the Google TV app, a no-go).
11. **Sun phase in its own file:** `web/sun.js` defines a global `Sun` (ES5) with `Sun.phase(nowMs, sunriseIso,
    sunsetIso)`, so `tests/WebSunTest.js` tests it in Node the way `tests/WebPrefsTest.js` tests `Prefs`;
    `webapp.files()` already packs every top-level file in `web/`. `index.html` loads it before `home.js`.
12. **Font licence in the package:** `webapp.files()` copies only `.woff2` from `web/fonts/`; it also copies
    `OFL-outfit-geist.txt` from there so the OFL travels with the fonts.
8. **Motion inventory (MOTION 7).** Entrance: clock, weather, shelf rise 24 px and fade in, 80 ms apart, 420 ms
   each (hierarchy). Shelf focus: 220 ms scale and label fade (feedback). Sky: 2 s crossfade between phase canvases
   (state transition). Drawer: the existing 380 ms slide (state transition). Transform and opacity only.
9. **Owner's build settings** live in the owner's `config.properties` (git-ignored): `city=Denver`,
   `latitude=39.73915`, `longitude=-104.9847`, `show_crypto=false`, `temperature=auto`.
10. **Delivery:** fork to `mcande21/free-my-tv`, push the branch, publish a release carrying the built
    `FreeMyTV-tizen.wgt` (unsigned); TizenBrew Installer installs it from the fork and re-signs it on Tizen 7+ with
    the owner's saved certificate, the same one as the current install, so it installs as an update.

13. **Version 1.5.1 in the fork:** `tizen/config.xml` `version="1.5.1"`, so the TV sees a newer package than the
    installed 1.5.0 and no same-version reinstall question arises. Rejected: shipping 1.5.0 again (untested path).

## Measurement method

The safe-margin and focus requirements are checked by the UI test from `getBoundingClientRect()` in headless Chrome
at a 1920 x 1080 window. It excludes the TV's own scaling and overscan; the TV check is a photo by the owner.

## Fail-closed branches

- No cached weather or a malformed body: the weather line is hidden and the sun phase falls back to clock hours; no
  exception escapes `renderPanels`.
- Canvas 2D context unavailable: the horizon is skipped and `#sky .night`/`.day` gradients show as today.
- Fonts fail to load: the stack falls back to `'Helvetica Neue', Arial, sans-serif`.
- TizenBrew re-sign fails: stop; the installed 1.5.0 stays; no uninstall without the owner's yes.

## Branches

- If a font's latin woff2 exceeds 60 KB, ship only the weights listed in Decision 2 and drop any extra.
- If the horizon canvas costs over 16 ms to draw on the TV (Web Inspector over SDB), lower its resolution to
  480 x 270.
- If `tools/check.sh web` flags a property used here, replace it with the nearest allowed form and note it.


## Names

New identifiers, grepped across `web/`, `tizen/`, `tools/` with `grep -rniw`: `horizon` 0 hits, `ridge` 0,
`alpenglow` 0, `sunphase` 0, `Sun` as a global: `grep -rnw "Sun" web` 1 hit, the string `'weekday|Sun'` at data.js:29, not an identifier: free. New CSS ids/classes: `#horizon`, `#weatherline`, `.wide`. `wide` already exists
(`.card.wide`, home.css:250) and is scoped by `.card`; the shelf uses `.tile.focus` instead, so no new `.wide`.

## Probe Ledger

| Assumption | Command | Result |
|---|---|---|
| Gate is green before the change | `tools/check.sh web` | exit 0, "All checks passed." |
| Web unit test green | `tools/test-web.sh` | exit 0, "WebPrefsTest: all checks passed." |
| Banned CSS list | `grep -n backdrop tools/check.sh` | line 45-47: custom properties, grid, backdrop-filter |
| Headless Chrome renders the page and its state | Chrome `--headless=new --dump-dom` on the served preview | `<body class="night no-picks no-key">`, #home, #top, #drawer present |
| Weather cache key and shape | `grep -n "store('weather'" web/data.js` | data.js:271 `{place, body, at, query}`; hourly and daily fields in the query, data.js:192-194 |
| Down on the shelf opens the drawer | `sed -n 1610,1620p web/home.js` | `else if (dy > 0) { openDrawer(); return; }` |
| Fonts are OFL, icons MIT | `npm view @fontsource/outfit @fontsource/geist-sans @phosphor-icons/web license` | OFL-1.1, OFL-1.1, MIT |
| Phosphor ships a regular TTF | `npm pack @phosphor-icons/web@2.1.2; tar tzf` | `package/src/regular/Phosphor.ttf` |
| Pillow present for the icon tool | `python3 -c "import PIL"` | missing: task 1.3 installs it in a throwaway venv |
| Installer re-signs on Tizen 7+ with the saved cert | read reisxd/TizenBrewInstaller index.js | `resignOrInstall`: `isTizen7OrHigher` then `resignPackage(certificates, buffer)` from config authorCert/distributorCert |
| Denver coordinates | Open-Meteo geocoding `name=Denver` | 39.73915, -104.9847, America/Denver |
| Symbols are shared with Android | `sed -n 97,130p tools/webapp.py` | `symbols = os.path.join(ROOT, 'app', 'assets', 'symbols')`: web packs the Android folder |
| New web/*.js files are packed | same read | `for name in sorted(os.listdir(web))`, files only: yes |
| web/fonts licence files are packed | same read | only `.woff2`: no; Decision 12 adds it |
| Installed version on the TV | `curl http://192.168.0.21:8001/api/v2/applications/FreeMyTVio.FreeMyTV` | `"version":"1.5.0"`; Decision 13 ships 1.5.1 |
| GitHub account for the fork | `gh api user -q .login` | mcande21 |
| Every place the font rule lives | `grep -rln Inter web docs` then `grep -rn "'Inter'" web` | web/home.css:12-17 (@font-face), :29 (body), :671 (body.rtl); home.js/tv.js hits are `setInterval`; docs/ out of scope, keeps its own |

## Rulings

- 2026-11-20: direction Front Range dusk; layout Horizon stage; delivery through the owner's fork. (Morpheus)
- 2026-11-21: plan approved with both simplify findings adopted: 2.1 tests that the old greys and black shadows are gone instead of one exact background; 3.5 tests transform/opacity only, no exact delays. (Morpheus)
