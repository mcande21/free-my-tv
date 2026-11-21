/*
 * The sky's phase for the horizon: 'night', 'dawn', 'day' or 'dusk', from today's sunrise and sunset (epoch ms, as
 * Data.weather holds them). Dawn runs from 45 minutes before sunrise to 30 after, dusk from 30 minutes before sunset
 * to 45 after. Without both times (none fetched yet, or 0 or NaN), the clock decides: night from 19:00 to 07:00.
 * ES5: older TVs run it.
 */
var Sun = (function () {
  var MIN = 60000;

  function known(t) { return typeof t === 'number' && isFinite(t) && t > 0; }

  function phase(now, sunrise, sunset) {
    if (!known(sunrise) || !known(sunset)) {
      var h = new Date(now).getHours();
      return h >= 19 || h < 7 ? 'night' : 'day';
    }
    if (now >= sunrise - 45 * MIN && now < sunrise + 30 * MIN) return 'dawn';
    if (now >= sunset - 30 * MIN && now < sunset + 45 * MIN) return 'dusk';
    return now >= sunrise + 30 * MIN && now < sunset - 30 * MIN ? 'day' : 'night';
  }

  return {phase: phase};
})();
