#!/usr/bin/env python3
"""Generate neofetch-style GitHub profile SVGs from me.png + editable fields below."""

from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageEnhance, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent

# --- Edit these ---
FIELDS = {
    "user": "mandy@hartman",
    "os": "macOS, iOS",
    "uptime": "XX years, XX months, XX days",
    "host": "Shift AI",
    "kernel": "AI Engineer",
    "ide": "Cursor, VS Code",
    "lang_prog": "TypeScript, Python, JavaScript",
    "lang_comp": "HTML, CSS, JSON, YAML, Markdown",
    "lang_real": "English",
    "hob_soft": "Building apps, Prompt engineering",
    "hob_hard": "Coffee gear, Desk setups",
    "email": "you@example.com",
    "website": "virtu-studios.com",
    "linkedin": "hartmandy",
    "discord": "your-discord",
    "repos": "59",
    "contrib": "XX",
    "stars": "XX",
    "commits": "X,XXX",
    "followers": "50",
    "loc": "XXX,XXX",
    "loc_add": "XXX,XXX",
    "loc_del": "XX,XXX",
}

# Face crop as fractions of (left, top, right, bottom)
CROP = (0.22, 0.00, 0.78, 0.55)
COLS, ROWS = 42, 25
CHARS = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"


def to_ascii(image_path: Path) -> list[str]:
    img = Image.open(image_path).convert("L")
    w, h = img.size
    left, top, right, bottom = (int(w * CROP[0]), int(h * CROP[1]), int(w * CROP[2]), int(h * CROP[3]))
    face = img.crop((left, top, right, bottom))
    face = ImageOps.autocontrast(face, cutoff=2)
    face = ImageEnhance.Contrast(face).enhance(1.55)
    face = ImageEnhance.Brightness(face).enhance(1.05)
    face = face.filter(ImageFilter.SHARPEN)
    face = face.resize((COLS, ROWS), Image.Resampling.LANCZOS)

    pixels = list(face.get_flattened_data())
    mn, mx = min(pixels), max(pixels)
    span = max(mx - mn, 1)
    gamma = 0.88

    lines: list[str] = []
    for y in range(ROWS):
        row = []
        for x in range(COLS):
            p = pixels[y * COLS + x]
            t = ((p - mn) / span) ** gamma
            v = 1.0 - t
            idx = int(round(max(0.0, min(1.0, v)) * (len(CHARS) - 1)))
            row.append(CHARS[idx])
        lines.append("".join(row))
    return lines


def kv(y: int, label: str, value: str, target_end: int = 52) -> str:
    parts = label.split(".")
    key_bits = []
    for i, part in enumerate(parts):
        if i:
            key_bits.append('<tspan class="key">.</tspan>')
        key_bits.append(f'<tspan class="key">{escape(part)}</tspan>')
    key_xml = "".join(key_bits)
    prefix_len = len(label) + 1
    dots_count = max(2, target_end - prefix_len - len(value))
    dots = " " + ("." * dots_count) + " "
    return (
        f'<tspan x="390" y="{y}" class="cc">. </tspan>{key_xml}:'
        f'<tspan class="cc">{dots}</tspan><tspan class="value">{escape(value)}</tspan>'
    )


def make_svg(ascii_lines: list[str], mode: str) -> str:
    if mode == "dark":
        bg, text, key, value, cc, add, delete = (
            "#161b22",
            "#c9d1d9",
            "#ffa657",
            "#a5d6ff",
            "#616e7f",
            "#3fb950",
            "#f85149",
        )
    else:
        bg, text, key, value, cc, add, delete = (
            "#ffffff",
            "#24292f",
            "#953800",
            "#0550ae",
            "#8c959f",
            "#1a7f37",
            "#cf222e",
        )

    width = max(len(line) for line in ascii_lines)
    ascii_lines = [line.ljust(width) for line in ascii_lines]
    ascii_tspants = [
        f'<tspan x="15" y="{30 + i * 20}">{escape(line)}</tspan>' for i, line in enumerate(ascii_lines)
    ]

    f = FIELDS
    right = [
        f'<tspan x="390" y="30">{escape(f["user"])}</tspan> -———————————————————————————————————————————-—-',
        kv(50, "OS", f["os"], 48),
        kv(70, "Uptime", f["uptime"], 48),
        kv(90, "Host", f["host"], 48),
        kv(110, "Kernel", f["kernel"], 48),
        kv(130, "IDE", f["ide"], 48),
        '<tspan x="390" y="150" class="cc">. </tspan>',
        kv(170, "Languages.Programming", f["lang_prog"], 52),
        kv(190, "Languages.Computer", f["lang_comp"], 52),
        kv(210, "Languages.Real", f["lang_real"], 52),
        '<tspan x="390" y="230" class="cc">. </tspan>',
        kv(250, "Hobbies.Software", f["hob_soft"], 52),
        kv(270, "Hobbies.Hardware", f["hob_hard"], 52),
        '<tspan x="390" y="310">- Contact</tspan> -——————————————————————————————————————————————-—-',
        kv(330, "Email.Personal", f["email"], 52),
        kv(350, "Website", f["website"], 52),
        kv(370, "LinkedIn", f["linkedin"], 52),
        kv(390, "Discord", f["discord"], 52),
        '<tspan x="390" y="450">- GitHub Stats</tspan> -—————————————————————————————————————————-—-',
        (
            f'<tspan x="390" y="470" class="cc">. </tspan><tspan class="key">Repos</tspan>:'
            f'<tspan class="cc"> .... </tspan><tspan class="value">{escape(f["repos"])}</tspan> {{'
            f'<tspan class="key">Contributed</tspan>: <tspan class="value">{escape(f["contrib"])}</tspan>}} | '
            f'<tspan class="key">Stars</tspan>:<tspan class="cc"> ........... </tspan>'
            f'<tspan class="value">{escape(f["stars"])}</tspan>'
        ),
        (
            f'<tspan x="390" y="490" class="cc">. </tspan><tspan class="key">Commits</tspan>:'
            f'<tspan class="cc"> ................. </tspan><tspan class="value">{escape(f["commits"])}</tspan> | '
            f'<tspan class="key">Followers</tspan>:<tspan class="cc"> ....... </tspan>'
            f'<tspan class="value">{escape(f["followers"])}</tspan>'
        ),
        (
            f'<tspan x="390" y="510" class="cc">. </tspan><tspan class="key">Lines of Code on GitHub</tspan>:'
            f'<tspan class="cc">. </tspan><tspan class="value">{escape(f["loc"])}</tspan> ( '
            f'<tspan class="addColor">{escape(f["loc_add"])}</tspan><tspan class="addColor">++</tspan>, '
            f'<tspan class="delColor">{escape(f["loc_del"])}</tspan><tspan class="delColor">--</tspan> )'
        ),
    ]

    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" font-family="ConsolasFallback,Consolas,monospace" width="985px" height="530px" font-size="16px">
<style>
@font-face {{
  src: local("Consolas"), local("Consolas Bold");
  font-family: "ConsolasFallback";
  font-display: swap;
  -webkit-size-adjust: 109%;
  size-adjust: 109%;
}}
.key {{ fill: {key}; }}
.value {{ fill: {value}; }}
.addColor {{ fill: {add}; }}
.delColor {{ fill: {delete}; }}
.cc {{ fill: {cc}; }}
text, tspan {{ white-space: pre; }}
</style>
<rect width="985px" height="530px" fill="{bg}" rx="15"/>
<text x="15" y="30" fill="{text}" class="ascii">
{chr(10).join(ascii_tspants)}
</text>
<text x="390" y="30" fill="{text}">
{chr(10).join(right)}
</text>
</svg>
'''


def main() -> None:
    image_path = ROOT / "me.png"
    if not image_path.exists():
        raise SystemExit("Missing me.png — drop your portrait next to generate.py")

    ascii_lines = to_ascii(image_path)
    (ROOT / "dark_mode.svg").write_text(make_svg(ascii_lines, "dark"))
    (ROOT / "light_mode.svg").write_text(make_svg(ascii_lines, "light"))
    print("Wrote dark_mode.svg and light_mode.svg")


if __name__ == "__main__":
    main()
