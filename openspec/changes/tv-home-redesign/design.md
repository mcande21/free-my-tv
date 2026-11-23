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
2. **Type: Outfit + Geist, local woff2.** Outfit 300 and 500 for headings, Outfit 400 for the time (Decision 17); Geist 400
   and 600 for interface text; `font-variant-numeric: tabular-nums` on the time and temperatures. Files from
   `@fontsource/outfit` 5.3.0 and `@fontsource/geist-sans` 5.3.0 (OFL-1.1), latin subset, with `OFL.txt` beside them.
   Inter stays in the stack after Geist (home.css:29 and :671) and its files stay, for Cyrillic, Greek and Vietnamese glyphs the latin subsets lack. Rejected: Inter as the face (the audit's first finding); deleting Inter (other languages would fall to system fonts); a CDN (the app runs offline and from file://).
3. **Front Range photographs, one per phase** (superseded the canvas ridges; ruling 2026-11-21). An `<img id="horizon">`
   in `#sky`, full bleed with `object-fit: cover`, shows `photos/<phase>.jpg` (1920 x 1080 JPEG, quality 90 from 2026-11-22, ruling photo-quality; was 78, cropped to
   the peaks). Its `error` handler hides it, so the `#sky .day`/`.night` gradients show. A dark gradient scrim
   (`#scrim`) sits over the photo behind the clock and the shelf, and with a photo shown the home text uses the night
   ink. Photos (Wikimedia Commons): dawn "Mt. Evans Sunset (5862299184).jpg", Zach Dischner, CC BY 2.0; day "Mount
   Meeker and Longs Peak.jpg", KamenG, CC BY-SA 4.0; dusk "Long's Peak Sunset.jpg", Peter Romero, CC BY-SA 4.0; night
   "Rocky Mountain National Park, United States (Unsplash pq2DJBntZW0).jpg", Jeremy Thomas, CC0. Rejected: the
   generated ridges (Morpheus wanted real photographs); city skylines (Morpheus: "focus on mountains not city").

4. **Sun phase** from `Data.weather.sunrise` and `.sunset` (epoch ms, which `parseWeather` makes from the cached `daily.sunrise[0]` and `daily.sunset[0]`): dawn = sunrise - 45 min to sunrise + 30 min;
   dusk = sunset - 30 min to sunset + 45 min; day between; night otherwise. No weather: night 19:00-07:00, else day.
5. **Weather line** reuses `weatherParts()` for the current reading and adds three hourly labels from
   `hourly.time`/`hourly.temperature_2m` after the current hour. Hidden when `Prefs.weather()` is false or no weather.
6. **Shelf focus** (amended 2026-11-21, ruling tiles-a) scales the whole focused tile to 1.08 (Android TV focus
   guidance: 1.025, 1.05 or 1.1) with a 3 px amber ring and an amber tinted glow, and fades in its name under it
   (opacity only); every tile keeps one box width so the row does not reflow. Replaces the underline and the
   icon-only scale. The tile's start-edge `pad` inside the safe area must cover the 4% growth (at least 10 px).
7. **Icons, web only:** the PNGs in `app/assets/symbols/` are shared with the Android app, so they stay. Phosphor
   renders into a new `web/symbols/` folder, and `tools/webapp.py` `files()` copies it after `app/assets/symbols/`,
   so a web name replaces the shared one in the LG and Samsung packages only. `tools/make_symbols.py` gains a Phosphor
   map (same app names, Phosphor regular glyph names) rendered from `Phosphor.ttf` of `@phosphor-icons/web` 2.1.2
   (MIT), `LICENSE-phosphor` beside them. Pillow runs from a throwaway virtualenv; a tool dependency only. Rejected:
   overwriting `app/assets/symbols/` (changes the Google TV app, a no-go).
11. **Sun phase in its own file:** `web/sun.js` defines a global `Sun` (ES5) with `Sun.phase(nowMs, sunriseMs,
    sunsetMs)`, falling back to clock hours when either time is missing, 0 or not a finite number, so `tests/WebSunTest.js` tests it in Node the way `tests/WebPrefsTest.js` tests `Prefs`;
    `webapp.files()` already packs every top-level file in `web/`. `index.html` loads it before `home.js`.
12. **Font licence in the package:** `webapp.files()` copies only `.woff2` from `web/fonts/`; it also copies
    `OFL-outfit-geist.txt` from there so the OFL travels with the fonts.
8. **Motion inventory (MOTION 7).** Entrance: clock, weather, shelf rise 24 px and fade in, 80 ms apart, 420 ms
   each (hierarchy). Shelf focus: 220 ms scale and label fade (feedback). Sky: 2 s crossfade between phase canvases
   (state transition). Drawer: the existing 380 ms slide (state transition). Transform and opacity only.
9. **Owner's build settings** live in the owner's `config.properties` (git-ignored): `city=Denver`,
   `latitude=39.73915`, `longitude=-104.9847`, `show_crypto=false`, `temperature=auto`; from 1.5.2
   `samsung_home_button=true` (ruling home-button): Home in an app opened from Free My TV brings it back.
10. **Delivery:** fork to `mcande21/free-my-tv`, push the branch, publish a release carrying the built
    `FreeMyTV-tizen.wgt` (unsigned); TizenBrew Installer installs it from the fork and re-signs it on Tizen 7+ with
    the owner's saved certificate, the same one as the current install, so it installs as an update.

14. **Photo credits:** `web/photos/CREDITS.txt` names each photo's author, source page, licence and the change made
    (cropped, resized). `tools/webapp.py` packs `web/photos/` (`.jpg` and `CREDITS.txt`). The two CC BY-SA crops are
    shared under CC BY-SA 4.0, which the credits file states.
15. **Readability measurement:** rendered 1920 x 1080 screenshots per phase; for each text box, the text colour against
    the median luminance of the pixels in the box's padding ring; WCAG contrast ratio. Excludes the TV's own picture
    processing.
13. **Version 1.5.1 in the fork:** `tizen/config.xml` `version="1.5.1"`, so the TV sees a newer package than the
    installed 1.5.0 and no same-version reinstall question arises. Rejected: shipping 1.5.0 again (untested path).
    Then 1.5.2 (ruling home-button) for the Home-button manifest, over the installed 1.5.1; if the TV refuses the
    upgrade, stop and ask before any uninstall.
16. **Shelf tiles share one surface** (ruling tiles-a, 2026-11-21). Six tiles at once (`SHELF_VISIBLE` 6), 16:9, at
   most 240 x 135; every tile is the same smoked slate `rgba(28, 33, 40, 0.62)` with a 1 px inset
   `rgba(236, 230, 220, 0.14)` line; no brand gradient on the shelf (the SHELF table's colours stay for All Apps).
   The face, in order: our white logo from `web/icons/mono/` when the app's SHELF key has one; else the app's own
   icon, centred on the slate; else its name as a white Geist 600 wordmark. White logos: Simple Icons 16.38.0 (CC0)
   with `fill="#FFFFFF"` for netflix, youtube, max, appletv, spotify, paramountplus, jellyfin, plex, twitch; Prime
   Video from our `icons/prime.png` turned white with its alpha kept. Simple Icons has no Prime Video, Disney+, Hulu,
   Peacock, Globoplay or NFL (404 at tag 16.38.0, checked 2026-11-21), so those take the wordmark unless the TV
   gives a real icon. Evidence: 00_research tv-home-designs.md F1, F5. Rejected: brand fill on focus (option B),
   brand banners (option C), a CSS `filter` to whiten (it flattens multi-colour logos).
17. **Type steps from tvOS** (ruling type-steps, 2026-11-21; Apple HIG typography: body 29, minimum 23, headline 38).
   Clock 160 px Outfit 400 (was 176 px 300); date 38 px Geist 500 (was 40); weather line 32 px on two lines, the
   current reading over the hours; focused app name 30 px Geist 600 (was 24). Nothing on the no-picks home under
   29 px. Adds `web/fonts/Outfit-400.woff2` from `@fontsource/outfit@5.3.0` (latin). Evidence: tv-home-designs.md F3.
18. **Tile depth, borrowed from tvOS, in our own CSS** (ruling tile-depth, 2026-11-22: simple and elegant; research
   00_research/tile-libraries.md: no library passes the ES5 gate). Four moves, amber stays the only colour:
   (a) the focused tile's logo or word lifts 4 px (`translateY(-4px)`) with `drop-shadow(0 6px 10px rgba(6, 10, 16, 0.5))`;
   (b) `.tile::after` becomes a top-left light over the whole tile, `rgba(255, 255, 255, 0.14)` to 0 at 60%, corners
   inherited, shown on focus only; (c) the focused tile adds `0 24px 48px rgba(6, 10, 16, 0.45)` under the amber
   glow; (d) every tile gets `inset 0 1px 0 rgba(255, 255, 255, 0.08)`. Transitions stay transform and opacity.
   Rejected: vanilla-tilt (patching a vendored copy), a moving sweep (busier than asked), brand-tinted glow (second
   accent against ruling tiles-a).
19. **Sharper photos** (rulings photo-quality, photo-picks, 2026-11-22; the owner saw softness on the 65" TV). Dawn
   becomes "Longs Peak from the Dream Lake trail at sunrise" (OKJaguar, CC BY-SA 4.0, 8886 x 3668) and day "Frosted
   Flatirons" (Zach Dischner, CC BY 2.0, 5180 x 3450): both cropped to 16:9 from the original file, resized once with
   Lanczos to 1920 x 1080, quality 90. Dusk and night ship their existing quality-90 1920 x 1080 crops
   (scratch/photos-src/*.crop.jpg), same framing. Cause, measured: the old dawn (2048 x 988) and day (2500 x 997) were
   under 1080 px tall and were enlarged; all four were quality 78. Kept at 1920 x 1080: the app draws a 1920 x 1080
   stage (web/index.html:5); whether the TV draws images above that is unknown.

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
| Photo licences and authors | Commons API extmetadata LicenseShortName, Artist | dawn CC BY 2.0 Zach Dischner; day CC BY-SA 4.0 KamenG; dusk CC BY-SA 4.0 Peter Romero; night CC0 Jeremy Thomas |
| Photo sizes allow a 1920 x 1080 crop | Commons API imageinfo size | dawn 2048x988 (upscale 9%), day 2500x997 (upscale 8%), dusk 2048x1365, night 5285x3513 |
| Installed version on the TV | `curl http://192.168.0.21:8001/api/v2/applications/FreeMyTVio.FreeMyTV` | `"version":"1.5.0"`; Decision 13 ships 1.5.1 |
| GitHub account for the fork | `gh api user -q .login` | mcande21 |
| Every place the font rule lives | `grep -rln Inter web docs` then `grep -rn "'Inter'" web` | web/home.css:12-17 (@font-face), :29 (body), :671 (body.rtl); home.js/tv.js hits are `setInterval`; docs/ out of scope, keeps its own |

## Rulings

- 2026-11-22: T2 amendment: sharper photos, new dawn and day, quality 90 (Decisions 3 and 19, task 3.13). (Morpheus: "Re-encode + new dawn/day"; picks Dream Lake sunrise and Frosted Flatirons)

- 2026-11-22: T2 amendment: tile depth from tvOS techniques in our CSS (Decision 18; task 3.12 added). (Morpheus: "borrow the technique, goal is simple and elegant")

- 2026-11-21: T2 amendment: Home button: build 1.5.2 with samsung_home_button=true, release v1.5.2-frontrange, install (Decisions 9 and 13; task 5.4 added). (Morpheus: "go for it" to rebuild, release and install; uninstall still needs his yes)

- 2026-11-21: T2 amendment: uniform shelf tiles with white logos and an amber ring, six 240 px tiles, tvOS type steps (Decisions 2 and 6 amended, 16-17 added; spec Shelf focus reworded, Shelf tiles share one surface and Type reads from the couch added; tasks 3.9-3.11 added, 5.1 reopened to rebuild). (Morpheus: tiles A, six larger, type all of it; research 00_research/tv-home-designs.md)

- 2026-11-20: direction Front Range dusk; layout Horizon stage; delivery through the owner's fork. (Morpheus)
- 2026-11-21: T2 amendment: Front Range photographs replace the canvas ridges (Decision 3, new 14-15; spec Horizon follows the sun reworded, Photo cannot load and Text stays readable added; task 3.6 superseded, 3.7-3.8 added). (Morpheus: photos, mountains not city, these four picks)
- 2026-11-21: T2 amendment: Sun.phase takes epoch ms, not ISO strings (Decisions 4 and 11, task 3.3); Data.weather already holds ms and data.js owns parsing. (Morpheus)
- 2026-11-21: plan approved with both simplify findings adopted: 2.1 tests that the old greys and black shadows are gone instead of one exact background; 3.5 tests transform/opacity only, no exact delays. (Morpheus)
