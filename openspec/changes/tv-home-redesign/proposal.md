## Intent

Restyle and re-lay-out the Free My TV home screen (the `web/` app that runs on Samsung Tizen and LG webOS) into one
look called **Front Range dusk**, for one household's 2024 Samsung UN65DU6900 in Denver, shipped from the owner's own
GitHub fork. End state: the TV opens to a dark slate screen with the time and Denver weather anchored left, a layered
mountain horizon across the lower half whose sky follows the real sun, and the app shelf along the bottom; one amber
accent marks focus. Appetite: one focused session of build work plus one install on the TV; light change; tier S.

## Why

The current home screen copies the Apple lock screen: Inter type, Apple system greys, no accent, and about 60% of the
screen empty in the no-picks state this household uses (no TMDB key). It reads as generic, and the owner asked for a
look and layout of his own.

## What Changes

- New type pairing: Outfit for the time and headings, Geist for interface text, both shipped as local woff2 files.
  Inter is removed from the home screen.
- New palette: warm slate neutrals with one amber accent; tinted shadows; a three-step corner radius scale.
- New no-picks layout ("Horizon stage"): time, date and a weather line (now plus the next three hours) at top left
  inside a 96 px / 54 px safe margin; a canvas-drawn horizon of three ridge layers across the lower half; the app
  shelf left-aligned along the bottom, where the focused app widens and shows its name; inputs and settings as two
  icon buttons at top right.
- The sky behind the horizon follows the sun: night, dawn, day, dusk colours chosen from today's sunrise and sunset.
- Icons re-rendered from Phosphor (regular weight) through the existing icon tool, replacing Material Symbols.
- Motion: a staggered entrance of clock, weather and shelf; focus growth on the shelf; a slow sky crossfade.
- The fork's release build turns crypto prices off and sets Denver as the city.
- A headless-browser UI test that loads the real page with fixed weather and checks the layout rules.
- The picks layout, the drawer, the settings sheets and the screensaver take the new type and colours only.

## Capabilities

### New Capabilities
- `home-screen`: what the TV home screen shows in the no-picks state, where it sits, how focus looks, and how the sky
  follows the sun.

### Modified Capabilities

## No-gos

- No changes to the Android (Google TV) app, the docs site, data fetching, settings logic or the switch to *Original*.
- No CSS custom properties, grid or backdrop-filter, and ES5 JavaScript only: older TVs run 2015-2017 Chromium.
- No pull request or push to the upstream repository.

## Rabbit holes

- A photographic or real-terrain horizon: the ridges are three generated silhouettes, not map data.
- Per-app brand art on the shelf: the shelf keeps the icons the TV supplies.

## Shared resources

| Artifact | Owner | How this change touches it |
|---|---|---|
| Upstream repo simbasjungles/free-my-tv | its author | read only; never pushed to |
| Fork mcande21/free-my-tv on GitHub | the owner (Morpheus) | created; the branch and a release are pushed to it with his yes |
| The owner's Samsung TV (192.168.0.21) | the owner | Free My TV is updated in place over Developer Mode |
| Samsung signing certificate in ~/share/tizenbrewInstallerConfig.json | the owner | read by TizenBrew Installer to re-sign; never copied or committed |
| Fonts (Outfit, Geist; OFL-1.1) and Phosphor icons (MIT) | their authors | vendored with licence files beside them |

## Impact

`web/home.css`, `web/index.html`, `web/home.js` (layout and the horizon), `web/fonts/`, the rendered icon PNGs,
`tools/make_symbols.py` (a Phosphor map), a new `tests/ui/` test, and the owner's local `config.properties`.
