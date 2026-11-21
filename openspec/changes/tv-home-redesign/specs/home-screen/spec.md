## Purpose

The TV home screen in the no-picks state: what it shows, where each part sits on a 1920 x 1080 screen, how the
focused item is marked, and how the background follows the sun.

## ADDED Requirements

### Requirement: Safe margin
Every readable or focusable element of the home screen SHALL sit inside the safe area: at least 96 px from the left
and right edges and 54 px from the top and bottom of the 1920 x 1080 stage. Background art MAY reach the edges.

#### Scenario: Elements inside the safe area
- **WHEN** the home screen opens in the no-picks state with weather loaded
- **THEN** the clock, the weather line, every shelf tile and the top-right buttons have bounding boxes inside x 96 to 1824 and y 54 to 1026

### Requirement: Clock and weather anchored top left
The home screen SHALL show the time, the date and one weather line at the top left: the current temperature and
condition, then the next three hours' temperatures.

#### Scenario: Weather line with forecast
- **WHEN** cached weather holds a current reading and at least three later hourly readings
- **THEN** the weather line shows the current temperature and condition followed by three hour labels with their temperatures, in the order of the hours

#### Scenario: No weather yet
- **WHEN** no weather has been fetched or cached
- **THEN** the weather line is hidden and the clock and date keep their places

#### Scenario: Weather turned off
- **WHEN** the weather preference is off in Home Settings
- **THEN** the weather line is hidden

### Requirement: Horizon follows the sun
The background SHALL draw a layered horizon whose sky colour comes from the sun's phase today: night, dawn, day or
dusk, worked out from the cached sunrise and sunset.

#### Scenario: Dusk colours after sunset
- **WHEN** the time is within 45 minutes after today's sunset
- **THEN** the sky shows the dusk palette

#### Scenario: No sunrise or sunset known
- **WHEN** no cached weather gives sunrise and sunset
- **THEN** the sky uses the night palette between 19:00 and 07:00 and the day palette otherwise

### Requirement: Shelf focus
The focused shelf tile SHALL be wider than the others, show its app name, and carry the amber accent; other tiles show
only their icons.

#### Scenario: Moving focus along the shelf
- **WHEN** focus moves from the first shelf tile to the second
- **THEN** the second tile is the only wide tile with a visible name, and the first returns to icon-only

### Requirement: Crypto prices off in this build
The home screen SHALL CONTINUE TO show crypto prices only when the build or Home Settings turns them on; the owner's
release build turns them off.

#### Scenario: Owner's build
- **WHEN** the page runs with show_crypto false
- **THEN** no price line appears on the home screen

### Requirement: Way back unchanged
The home screen SHALL CONTINUE TO open the drawer, Home Settings and every shelf app with the same remote keys as
before the change.

#### Scenario: Drawer still opens
- **WHEN** the down key is pressed with focus on the shelf
- **THEN** the drawer opens as it did before the change
