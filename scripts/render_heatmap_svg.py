"""Render data/contributions.json as an animated, terminal-style heatmap SVG.

Animation rules (GitHub's camo proxy ignores CSS keyframes, so SMIL only):
- every element's static attributes are its FINAL visible state
- elements are hidden only by a running <animate>, which starts at 0.01s,
  so a frozen/cached timeline still shows the finished picture
"""

import datetime as dt
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"

CELL, GAP = 11, 3
PAD_X, PAD_TOP = 40, 58
COLORS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
BG, FG, DIM, GREEN = "#0d1117", "#c9d1d9", "#8b949e", "#39d353"
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
# no < > & so the SVG stays valid XML
RAIN_GLYPHS = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄ0123456789Z:."
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"


def main() -> None:
    data = json.loads(DATA.read_text())
    days = data["days"]
    start = dt.date.fromisoformat(days[0]["date"])
    # LEARN: shift so column 0 starts on a Sunday, like GitHub's grid
    first_sunday = start - dt.timedelta(days=(start.weekday() + 1) % 7)

    cells, month_labels, seen_months = [], [], set()
    weeks = 0
    for d in days:
        date = dt.date.fromisoformat(d["date"])
        offset = (date - first_sunday).days
        col, row = offset // 7, offset % 7
        weeks = max(weeks, col + 1)
        x, y = PAD_X + col * (CELL + GAP), PAD_TOP + row * (CELL + GAP)
        # left-to-right sweep; each cell flashes bright then settles to its level
        begin = 0.01 + col * 0.035 + row * 0.01
        color = COLORS[d["level"]]
        anim = (
            f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;0.5;1" '
            f'dur="{begin + 0.3:.2f}s" begin="0.01s" fill="freeze"/>'
        )
        if d["level"] > 0:
            anim += (
                f'<animate attributeName="fill" values="{GREEN};{color}" dur="0.6s" '
                f'begin="{begin + 0.3:.2f}s" fill="freeze"/>'
            )
        if d["level"] >= 3:  # hot cells shimmer forever
            anim += (
                f'<animate attributeName="opacity" values="1;0.55;1" dur="{2.5 + (col % 5) * 0.4:.1f}s" '
                f'begin="{begin + 1:.2f}s" repeatCount="indefinite"/>'
            )
        cells.append(
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}">'
            f'<title>{d["count"]} on {d["date"]}</title>{anim}</rect>'
        )
        if date.day <= 7 and row == 0 and (date.year, date.month) not in seen_months:
            seen_months.add((date.year, date.month))
            month_labels.append(
                f'<text x="{x}" y="{PAD_TOP - 8}" fill="{DIM}" font-size="10">{MONTHS[date.month - 1]}</text>'
            )

    width = PAD_X + weeks * (CELL + GAP) + 24
    grid_h = 7 * (CELL + GAP)
    height = PAD_TOP + grid_h + 56
    total_text = f"{data['total']} contributions in the last year"
    text_w = (len(total_text) + 2) * 8  # +2 for the "> " prompt
    ty = PAD_TOP + grid_h + 30

    day_labels = "".join(
        f'<text x="{PAD_X - 30}" y="{PAD_TOP + r * (CELL + GAP) + 9}" fill="{DIM}" font-size="10">{n}</text>'
        for r, n in ((1, "Mon"), (3, "Wed"), (5, "Fri"))
    )
    legend_x = width - 24 - 5 * (CELL + GAP) - 70
    legend = f'<text x="{legend_x}" y="{ty}" fill="{DIM}" font-size="10">less</text>' + "".join(
        f'<rect x="{legend_x + 28 + i * (CELL + GAP)}" y="{ty - 9}" width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>'
        for i, c in enumerate(COLORS)
    ) + f'<text x="{legend_x + 32 + 5 * (CELL + GAP)}" y="{ty}" fill="{DIM}" font-size="10">more</text>'

    # Matrix rain: faint glyph columns that fall in discrete steps (cheap on CPU).
    # LEARN: fixed seed so the daily rebuild doesn't change the SVG unless data changed
    rng = random.Random(381)
    rain = []
    for _ in range(26):
        x = rng.randint(PAD_X, width - 30)
        glyphs = "".join(rng.choice(RAIN_GLYPHS) for _ in range(rng.randint(5, 10)))
        tspans = "".join(f'<tspan x="{x}" dy="13">{g}</tspan>' for g in glyphs)
        steps = 16
        ys = ";".join(f"0,{-140 + i * (height + 140) // steps}" for i in range(steps + 1))
        rain.append(
            f'<text y="0" fill="{GREEN}" font-size="11" opacity="{rng.uniform(0.08, 0.2):.2f}">{tspans}'
            f'<animateTransform attributeName="transform" type="translate" values="{ys}" calcMode="discrete" '
            f'dur="{rng.uniform(3, 7):.1f}s" begin="{rng.uniform(0.01, 4):.2f}s" repeatCount="indefinite"/></text>'
        )

    sweep_end = 0.01 + weeks * 0.035 + 0.6
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" font-family="{FONT}">
<rect width="100%" height="100%" rx="10" fill="{BG}" stroke="#30363d"/>
<clipPath id="frame"><rect width="100%" height="100%" rx="10"/></clipPath>
<g clip-path="url(#frame)">{''.join(rain)}</g>
<circle cx="18" cy="16" r="5" fill="#ff5f56"/><circle cx="34" cy="16" r="5" fill="#ffbd2e"/><circle cx="50" cy="16" r="5" fill="#27c93f"/>
<text x="68" y="20" fill="{DIM}" font-size="11">~/{data['username']} $ git log --graph --since="1 year ago"</text>
{''.join(month_labels)}{day_labels}
{''.join(cells)}
<rect x="{PAD_X - 4}" y="{PAD_TOP - 4}" width="3" height="{grid_h + 4}" fill="{GREEN}" opacity="0">
<animate attributeName="x" values="{PAD_X - 4};{width - 24}" dur="{sweep_end:.2f}s" begin="0.01s"/>
<animate attributeName="opacity" values="0.7;0.7;0" keyTimes="0;0.95;1" dur="{sweep_end:.2f}s" begin="0.01s"/>
</rect>
<clipPath id="type"><rect x="{PAD_X}" y="{ty - 14}" width="{text_w:.0f}" height="20">
<animate attributeName="width" values="0;0;{text_w:.0f}" keyTimes="0;0.6;1" dur="{sweep_end + 1.2:.2f}s" begin="0.01s"/>
</rect></clipPath>
<text x="{PAD_X}" y="{ty}" fill="{FG}" font-size="13" clip-path="url(#type)"><tspan fill="{GREEN}">&gt;</tspan> {total_text}</text>
<rect x="{PAD_X + text_w + 14:.0f}" y="{ty - 11}" width="8" height="14" fill="{GREEN}">
<animate attributeName="opacity" values="1;0" dur="1s" calcMode="discrete" repeatCount="indefinite" begin="0.01s"/>
</rect>
{legend}
</svg>
"""
    OUT.write_text(svg)
    print(f"wrote {OUT} ({width}x{height})")


if __name__ == "__main__":
    main()
