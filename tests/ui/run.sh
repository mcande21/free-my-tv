#!/usr/bin/env bash
# Runs the home screen's UI cases in headless Chrome against the Tizen preview build (python3 tizen/build.py --preview).
# Each case loads tests/ui/harness.html?case=<name>, which opens the real page in a same-origin iframe and writes
# "PASS <name>" or "FAIL <name>: <why>" into #result. Needs Google Chrome (or $CHROME) and Python 3.
#   tests/ui/run.sh            # every case
#   tests/ui/run.sh <case>...  # only these
set -euo pipefail
cd "$(dirname "$0")/../.."
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
PORT="${UI_PORT:-8766}"
[ -x "$CHROME" ] || { echo "tests/ui: Chrome not found at $CHROME (set CHROME)" >&2; exit 2; }
python3 tizen/build.py --preview >/dev/null
python3 -m http.server "$PORT" --bind 127.0.0.1 >/dev/null 2>&1 &
server=$!
profile="$(mktemp -d)"
trap 'st=$?; kill $server 2>/dev/null; wait $server 2>/dev/null || true; rm -rf "$profile"; exit $st' EXIT
for i in $(seq 1 50); do curl -s -o /dev/null "http://127.0.0.1:$PORT/tests/ui/harness.html" && break; sleep 0.1; done
cases=("$@")
[ ${#cases[@]} -gt 0 ] || cases=($(grep -oE "^  '[a-z0-9-]+': \{" tests/ui/harness.html | tr -d "': {"))
[ ${#cases[@]} -gt 0 ] || { echo "tests/ui: no cases found" >&2; exit 2; }
failed=0
for c in "${cases[@]}"; do
  # Offline but for this server: cases run on their seeded data only, never on live weather or prices.
  out="$("$CHROME" --headless=new --disable-gpu --hide-scrollbars --user-data-dir="$profile/$c" \
    --host-resolver-rules="MAP * ~NOTFOUND, EXCLUDE 127.0.0.1" \
    --window-size=1920,1080 --virtual-time-budget=10000 --dump-dom \
    "http://127.0.0.1:$PORT/tests/ui/harness.html?case=$c" 2>/dev/null)"
  line="$(printf '%s' "$out" | sed -n 's/.*<pre id="result">\([^<]*\)<\/pre>.*/\1/p')"
  case "$line" in
    "PASS $c") echo "PASS $c" ;;
    "FAIL $c"*) echo "$line"; failed=$((failed + 1)) ;;
    *) echo "FAIL $c: ${line:-no result written}"; failed=$((failed + 1)) ;;
  esac
done
echo "tests/ui: $(( ${#cases[@]} - failed )) passed, $failed failed"
[ "$failed" -eq 0 ]
