"""Build the neofetch-style info-card.svg.

The card is displayed at 440px wide next to the GIF (320px wide). Its aspect
ratio is chosen so its displayed height equals the GIF's, keeping columns aligned.
"""

import textwrap
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "info-card.svg"

GIF_W, GIF_H, GIF_DISPLAY_W = 200, 188, 320
CARD_DISPLAY_W = 440
VIEW_W = 560
# LEARN: viewBox height scaled so 440px-wide card renders exactly as tall as the GIF
VIEW_H = round(GIF_H * GIF_DISPLAY_W / GIF_W * VIEW_W / CARD_DISPLAY_W)

FIELDS = [
    ("OS", "Ubuntu · macOS · Windows (yes, all three. no, I won't pick)"),
    ("Host", "ramzan_381"),
    ("Kernel", "Python · Java · Liquid · C++ (the C++ is for grades)"),
    ("Uptime", "battling sleep"),
    ("Shell", "Istanbul (for now)"),
    ("Packages", "Next.js · React · Supabase · PyTorch · PHP"),
    ("Research", "catching IoT botnets with tiny neural nets"),
    ("Projects", "Some websites here and there · Third Brain (my AI's memory) · AI maxing"),
    ("Day job", "selling socks to conscious consumers (hipSwan)"),
    ("Side quest", "always ongoing"),
    ("Status", "hunting a Master's in EU"),
    ("Web", "ramzanahmad.com (under construction)"),
]

BG, FG, KEY, DIM, GREEN = "#0d1117", "#c9d1d9", "#58a6ff", "#8b949e", "#39d353"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
LINE_H, X0, VAL_X, WRAP = 19, 20, 120, 52


def main() -> None:
    lines: list[str] = []
    y = 46

    def add(content: str) -> None:
        nonlocal y
        # each line types in one after another; static state = visible
        n = len(lines)
        lines.append(
            f'<g>{content}<animate attributeName="opacity" values="0;0;1" '
            f'keyTimes="0;{n / (n + 1):.3f};1" dur="{0.2 + n * 0.12:.2f}s" begin="0.01s"/></g>'
        )
        y += LINE_H

    add(f'<text x="{X0}" y="{y}" font-size="14" font-weight="bold"><tspan fill="{GREEN}">ramzan</tspan><tspan fill="{FG}">@</tspan><tspan fill="{GREEN}">CadPosting</tspan></text>')
    add(f'<text x="{X0}" y="{y - 6}" fill="{DIM}" font-size="13">{"-" * 17}</text>')
    for key, value in FIELDS:
        chunks = textwrap.wrap(value, WRAP)
        first = f'<text x="{X0}" y="{y}" font-size="13"><tspan fill="{KEY}" font-weight="bold">{escape(key)}:</tspan><tspan x="{VAL_X}" fill="{FG}">{escape(chunks[0])}</tspan></text>'
        add(first)
        for chunk in chunks[1:]:
            add(f'<text x="{VAL_X}" y="{y}" fill="{FG}" font-size="13">{escape(chunk)}</text>')

    palette = "".join(
        f'<rect x="{X0 + i * 22}" y="{y - 8}" width="20" height="10" fill="{c}"/>'
        for i, c in enumerate(["#ff5f56", "#ffbd2e", "#27c93f", "#58a6ff", "#bc8cff", "#39d353", "#c9d1d9"])
    )
    cursor = (
        f'<rect x="{X0 + 7 * 22 + 8}" y="{y - 10}" width="9" height="15" fill="{GREEN}">'
        f'<animate attributeName="opacity" values="1;0" dur="1s" calcMode="discrete" repeatCount="indefinite" begin="0.01s"/></rect>'
    )
    if y + 10 > VIEW_H:
        raise SystemExit(f"Card content ({y}px) overflows height {VIEW_H}; shorten FIELDS")

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{VIEW_W}" height="{VIEW_H}" viewBox="0 0 {VIEW_W} {VIEW_H}" font-family="{FONT}">
<rect x="0.5" y="0.5" width="{VIEW_W - 1}" height="{VIEW_H - 1}" rx="10" fill="{BG}" stroke="#30363d"/>
<circle cx="18" cy="16" r="5" fill="#ff5f56"/><circle cx="34" cy="16" r="5" fill="#ffbd2e"/><circle cx="50" cy="16" r="5" fill="#27c93f"/>
<text x="68" y="20" fill="{DIM}" font-size="11">~ $ neofetch</text>
{chr(10).join(lines)}
{palette}{cursor}
</svg>
"""
    OUT.write_text(svg)
    print(f"wrote {OUT} ({VIEW_W}x{VIEW_H}, content ends at y={y})")


if __name__ == "__main__":
    main()
