import re
from collections.abc import Sequence
from pathlib import Path

NAMES = [
    "bg-0",
    "bg-1",
    "bg-2",
    "dim",
    "fg-0",
    "fg-1",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "orange",
    "violet",
    "br-red",
    "br-green",
    "br-yellow",
    "br-blue",
    "br-magenta",
    "br-cyan",
    "br-orange",
    "br-violet",
]

_LIGHT = [
    "#fbf3db",
    "#ece3cc",
    "#d5cdb6",
    "#909995",
    "#53676d",
    "#3a4d53",
    "#d2212d",
    "#489100",
    "#ad8900",
    "#0072d4",
    "#ca4898",
    "#009c8f",
    "#c25d1e",
    "#8762c6",
    "#cc1729",
    "#428b00",
    "#a78300",
    "#006dce",
    "#c44392",
    "#00978a",
    "#bc5819",
    "#825dc0",
]

_DARK = [
    "#103c48",
    "#184956",
    "#2d5b69",
    "#72898f",
    "#adbcbc",
    "#cad8d9",
    "#fa5750",
    "#75b938",
    "#dbb32d",
    "#4695f7",
    "#f275be",
    "#41c7b9",
    "#ed8649",
    "#af88eb",
    "#ff665c",
    "#84c747",
    "#ebc13d",
    "#58a3ff",
    "#ff84cd",
    "#53d6c7",
    "#fd9456",
    "#bd96fa",
]

NAME_MAP = {
    "base": "bg-0",
    "mantle": "bg-1",
    "crust": "bg-1",
    "surface0": "bg-2",
    "surface1": "grey-1",
    "surface2": "grey-2",
    "overlay0": "dim",
    "overlay1": "grey-3",
    "subtext0": "grey-3",
    "overlay2": "grey-4",
    "subtext1": "grey-4",
    "text": "fg-1",
    "pink": "magenta",
    "flamingo": "magenta",
    "rosewater": "orange",
    "peach": "orange",
    "lavender": "violet",
    "mauve": "violet",
    "sapphire": "cyan",
    "teal": "cyan",
    "sky": "cyan",
    "maroon": "br-red",
    "red": "red",
    "green": "green",
    "yellow": "yellow",
    "blue": "blue",
}


def _channels(color: str) -> list[int]:
    return [int(color[i : i + 2], 16) for i in (1, 3, 5)]


def mix(a: str, b: str, t: float) -> str:
    mixed = (int(x + (y - x) * t + 0.5) for x, y in zip(_channels(a), _channels(b)))
    return "#" + "".join(f"{c:02x}" for c in mixed)


def _luminance(color: str) -> float:
    r, g, b = (
        c / 255 / 12.92 if c / 255 <= 0.04045 else ((c / 255 + 0.055) / 1.055) ** 2.4
        for c in _channels(color)
    )
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    hi, lo = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def _palette(values: Sequence[str]) -> dict[str, str]:
    p: dict[str, str] = dict(zip(NAMES, values))
    p["grey-1"] = mix(p["bg-2"], p["dim"], 1 / 3)
    p["grey-2"] = mix(p["bg-2"], p["dim"], 2 / 3)
    p["grey-3"] = mix(p["dim"], p["fg-0"], 1 / 3)
    p["grey-4"] = mix(p["dim"], p["fg-0"], 2 / 3)
    return p


PALETTES = {"light": _palette(_LIGHT), "dark": _palette(_DARK)}


APPENDED_RULES = """

.filter-item.dropdown:not(.filter_item_icon, .filter_item_single):is(:focus-within, :hover) {
  background: color-mix(in srgb, var(--violet) 30%, var(--bg-0));
  color: var(--fg-1);
}

.k_ui_toggle_switch input:checked ~ .k_ui_toggle_switch_bar {
  background: var(--br-green);
  border-color: var(--br-green);
}

.k_ui_toggle_switch input:checked ~ .k_ui_toggle_switch_bar::after {
  background-color: var(--bg-0);
}

._0_d_info_ranking.k_ui_btn_group {
  background-color: var(--bg-2);
  color: var(--fg-1);
}

._0_d_info_ranking.k_ui_btn_group .k_ui_btn {
  color: var(--fg-1);
}

._0_d_info_ranking.k_ui_btn_group #domain_rank_ban + .k_ui_btn {
  color: var(--fg-1);
}

._0_d_info_ranking.k_ui_btn_group .k_ui_btn:hover,
._0_d_info_ranking.k_ui_btn_group input:checked + .k_ui_btn {
  background-color: var(--fg-1);
  color: var(--bg-0);
}

._0_d_info_ranking.k_ui_btn_group #domain_rank_ban + .k_ui_btn:hover,
._0_d_info_ranking.k_ui_btn_group #domain_rank_ban:checked + .k_ui_btn {
  background-color: var(--br-red);
  color: var(--bg-0);
}

._0_d_info_ranking.k_ui_btn_group #domain_rank_boost + .k_ui_btn:hover,
._0_d_info_ranking.k_ui_btn_group #domain_rank_boost:checked + .k_ui_btn {
  background-color: var(--br-blue);
  color: var(--bg-0);
}

.ranking-note {
  background-color: var(--bg-2);
  color: var(--fg-1);
}
"""

_PALETTE_DECL = re.compile(
    r"^(\s*)--(?:" + "|".join(NAME_MAP) + r"):\s*#[0-9a-fA-F]{6};\s*$"
)
_RULE_OPEN = re.compile(r"^\s*([^{}]*?)\s*\{\s*$")
_DECL = re.compile(r"^\s*--([\w-]+)\s*:")
_OLD_REF = re.compile(r"var\(--(" + "|".join(NAME_MAP) + r")(?=[,)])")
_BASE_ALPHA = re.compile(r"rgba\(30, 30, 46, ([\d.]+)\)")


def _variant(selector: str) -> str:
    return "light" if selector == ":root" else "dark"


def convert(css: str) -> str:
    out: list[str] = []
    selector = ""
    in_palette_run = False
    for line in css.split("\n"):
        if match := _RULE_OPEN.match(line):
            selector = match.group(1)
        palette_line = _PALETTE_DECL.match(line)
        if palette_line:
            if not in_palette_run:
                indent = palette_line.group(1)
                out.extend(
                    f"{indent}--{name}: {value};"
                    for name, value in PALETTES[_variant(selector)].items()
                )
            in_palette_run = True
            continue
        in_palette_run = False
        if (decl := _DECL.match(line)) and decl.group(1) in PALETTES["light"]:
            raise ValueError(f"--{decl.group(1)} is already declared in the source")
        line = _OLD_REF.sub(lambda m: f"var(--{NAME_MAP[m.group(1)]}", line)
        line = _BASE_ALPHA.sub(
            lambda m: (
                f"color-mix(in srgb, var(--bg-0) {float(m.group(1)) * 100:g}%, transparent)"
            ),
            line,
        )
        out.append(line)
    return "\n".join(out) + APPENDED_RULES


def main(src: Path, dst: Path) -> None:
    dst.write_text(convert(src.read_text(encoding="utf-8")), encoding="utf-8")


if __name__ == "__main__":
    import sys

    main(Path(sys.argv[1]), Path(sys.argv[2]))
