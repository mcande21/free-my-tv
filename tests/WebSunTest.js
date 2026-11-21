/*
 * The sky's phase (web/sun.js): night, dawn, day or dusk from today's sunrise and sunset, or from the clock when they
 * are unknown. Expected phases derived by hand for sunrise 06:58 and sunset 16:40: dawn 06:13 to 07:28, dusk 16:10
 * to 17:25 (start included, end excluded); without times, night 19:00 to 07:00. Run by tools/test-web.sh.
 */
'use strict';
var fs = require('fs'), path = require('path'), vm = require('vm');

var sandbox = {};
vm.runInNewContext(fs.readFileSync(path.join(__dirname, '..', 'web', 'sun.js'), 'utf8'), sandbox, {filename: 'web/sun.js'});
var Sun = sandbox.Sun;

function at(h, m) { return new Date(2026, 10, 21, h, m || 0).getTime(); }
var RISE = at(6, 58), SET = at(16, 40);

var failures = 0;
function expect(name, got, want) {
  if (got !== want) { failures++; console.log('FAIL ' + name + ': expected ' + want + ', got ' + got); }
}

expect('dusk after sunset', Sun.phase(at(17, 0), RISE, SET), 'dusk');
expect('night once dusk ends', Sun.phase(at(17, 30), RISE, SET), 'night');
expect('dawn before sunrise', Sun.phase(at(6, 30), RISE, SET), 'dawn');
expect('day at noon', Sun.phase(at(12, 0), RISE, SET), 'day');
expect('dusk starts 30 min before sunset', Sun.phase(at(16, 10), RISE, SET), 'dusk');
expect('dusk ends 45 min after sunset', Sun.phase(at(17, 25), RISE, SET), 'night');
expect('dawn starts 45 min before sunrise', Sun.phase(at(6, 13), RISE, SET), 'dawn');
expect('dawn ends 30 min after sunrise', Sun.phase(at(7, 28), RISE, SET), 'day');
expect('no times: night at 20:00', Sun.phase(at(20, 0)), 'night');
expect('no times: day at noon', Sun.phase(at(12, 0)), 'day');
expect('no times: day from 07:00', Sun.phase(at(7, 0)), 'day');
expect('no times: night from 19:00', Sun.phase(at(19, 0)), 'night');
expect('zero times use the clock, not 1970', Sun.phase(at(18, 0), 0, 0), 'day');
expect('NaN times use the clock', Sun.phase(at(18, 0), NaN, NaN), 'day');
expect('one time missing uses the clock', Sun.phase(at(18, 0), RISE, undefined), 'day');

if (failures) { console.log('WebSunTest: ' + failures + ' failed'); process.exit(1); }
console.log('WebSunTest: all checks passed.');
