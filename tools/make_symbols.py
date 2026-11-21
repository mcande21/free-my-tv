"""Renders the icons (white PNGs with transparency) from the Material Symbols Rounded font, or with --set phosphor from
Phosphor's regular font (the web build's icons, web/symbols; the Android app keeps Material in app/assets/symbols).
Usage: python3 -I make_symbols.py FONT.ttf CODEPOINTS OUT_DIR [EM_PX] [--set phosphor]
  CODEPOINTS: Material's "name hex" codepoints file, or for Phosphor its IcoMoon selection.json."""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# name used in the app -> (Material Symbols name, filled?)
MAP = {
    "sunny": ("sunny", 1), "clear_night": ("clear_night", 1), "partly_cloudy_day": ("partly_cloudy_day", 1),
    "partly_cloudy_night": ("partly_cloudy_night", 1), "cloud": ("cloud", 1), "foggy": ("foggy", 1),
    "rainy": ("rainy", 1),
    "thunderstorm": ("thunderstorm", 1), "snowflake": ("ac_unit", 0),
    "tv": ("tv", 0), "gamepad": ("sports_esports", 1), "hdmi": ("settings_input_hdmi", 1),
    "apps": ("apps", 1), "settings": ("settings", 1), "speaker": ("speaker", 1),
    "store": ("shopping_bag", 0),
    "sparkles": ("auto_awesome", 1), "bedtime": ("bedtime", 1), "home": ("home", 1),
    "chevron_right": ("chevron_right", 0), "bell": ("notifications", 1), "sync": ("sync", 0),
    "check": ("check", 0), "play": ("play_arrow", 1), "tv_settings": ("display_settings", 1),
    "chevron_down": ("keyboard_arrow_down", 0), "sunrise": ("wb_twilight", 1), "sunset": ("wb_twilight", 1),
    "live_tv": ("live_tv", 1), "bitcoin": ("currency_bitcoin", 0), "recents": ("view_carousel", 0),
    "wifi": ("wifi", 1), "ethernet": ("lan", 1), "bluetooth": ("bluetooth_connected", 1), "usb": ("usb", 1),
    "keystone": ("settings_overscan", 1), "cast": ("cast", 1),
    "accessibility": ("accessibility_new", 0),
    "lightbulb": ("lightbulb", 1), "toggle": ("toggle_on", 1), "fan": ("mode_fan", 1), "blinds": ("blinds", 1),
    "bolt": ("bolt", 1), "smart_button": ("smart_button", 1),
}

# The same app names -> (Phosphor regular name, unused). Phosphor has no blinds: rows reads as slats.
PHOSPHOR = {
    "sunny": ("sun", 0), "clear_night": ("moon-stars", 0), "partly_cloudy_day": ("cloud-sun", 0),
    "partly_cloudy_night": ("cloud-moon", 0), "cloud": ("cloud", 0), "foggy": ("cloud-fog", 0),
    "rainy": ("cloud-rain", 0), "thunderstorm": ("cloud-lightning", 0), "snowflake": ("snowflake", 0),
    "tv": ("television-simple", 0), "gamepad": ("game-controller", 0), "hdmi": ("plugs", 0),
    "apps": ("squares-four", 0), "settings": ("gear-six", 0), "speaker": ("speaker-hifi", 0),
    "store": ("shopping-bag", 0), "sparkles": ("sparkle", 0), "bedtime": ("moon", 0), "home": ("house", 0),
    "chevron_right": ("caret-right", 0), "bell": ("bell", 0), "sync": ("arrows-clockwise", 0),
    "check": ("check", 0), "play": ("play", 0), "tv_settings": ("monitor", 0),
    "chevron_down": ("caret-down", 0), "sunrise": ("sun-horizon", 0), "sunset": ("sun-horizon", 0),
    "live_tv": ("television", 0), "bitcoin": ("currency-btc", 0), "recents": ("cards", 0),
    "wifi": ("wifi-high", 0), "ethernet": ("network", 0), "bluetooth": ("bluetooth-connected", 0), "usb": ("usb", 0),
    "keystone": ("frame-corners", 0), "cast": ("screencast", 0), "accessibility": ("person-arms-spread", 0),
    "lightbulb": ("lightbulb", 0), "toggle": ("toggle-right", 0), "fan": ("fan", 0), "blinds": ("rows", 0),
    "bolt": ("lightning", 0), "smart_button": ("hand-tap", 0),
}


def read_codes(cp_path):
    """Glyph name -> codepoint, from Material's "name hex" lines or an IcoMoon selection.json (Phosphor)."""
    codes = {}
    if cp_path.endswith(".json"):
        import json
        for icon in json.load(open(cp_path, encoding="utf-8"))["icons"]:
            for n in icon["properties"]["name"].split(","):
                codes[n.strip()] = icon["properties"]["code"]
        return codes
    for line in open(cp_path, encoding="utf-8"):
        parts = line.split()
        if len(parts) == 2:
            codes[parts[0]] = int(parts[1], 16)
    return codes


def main():
    args = [a for a in sys.argv[1:] if a != "--set" and a != "phosphor"]
    table = PHOSPHOR if "phosphor" in sys.argv[1:] else MAP
    font_path, cp_path, out = args[0], args[1], args[2]
    em = int(args[3]) if len(args) > 3 else 172
    codes = read_codes(cp_path)
    os.makedirs(out, exist_ok=True)
    big_font = ImageFont.truetype(font_path, em * 8)
    try:
        axes = [a["name"] if isinstance(a["name"], str) else a["name"].decode() for a in big_font.get_variation_axes()]
    except OSError:   # not a variable font
        axes = []
    for name, (material, fill) in table.items():
        values = []
        for axis in axes:
            a = axis.lower()
            values.append(fill if "fill" in a else 0 if "grad" in a else 48 if "optical" in a or "opsz" in a else 600)
        big_font.set_variation_by_axes(values)
        ch = chr(codes[material])
        # Drawn 8x larger without smoothing (the variable font's overlapping contours leave no gaps), then scaled down.
        big = Image.new("L", (em * 16, em * 16), 0)
        draw = ImageDraw.Draw(big)
        draw.fontmode = "1"
        draw.text((em * 4, em * 4), ch, font=big_font, fill=255)
        # Closes the hairline gaps between the variable font's outline and its fill (dilate, then erode). A static font
        # (Phosphor) has no overlapping contours, and closing would fill its thin outlines' holes.
        if axes:
            big = big.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.MinFilter(9))
        box = big.getbbox()
        pad = 16
        big = big.crop((box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad))
        img = big.resize((max(1, round(big.width / 8)), max(1, round(big.height / 8))), Image.LANCZOS)
        rgba = Image.new("RGBA", img.size, (255, 255, 255, 0))
        rgba.putalpha(img)
        rgba.save(os.path.join(out, name + ".png"), optimize=True)
    print("ok:", len(table), "icons in", out, "axes:", axes)


if __name__ == "__main__":
    main()
