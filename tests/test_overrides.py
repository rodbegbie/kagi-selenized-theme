import re

import pytest

from build_theme import PALETTES, contrast, convert, mix

FIXTURE = """\
:root {
  --text: #4c4f69;
  --base: #eff1f5;
  --mauve: #8839ef;
  --dd-hover-bg: var(--mauve);
  --dd-hover-color: var(--text);
}

.theme_moon_dark {
  --text: #cdd6f4;
  --base: #1e1e2e;
  --mauve: #cba6f7;
}
"""

DROPDOWN_HOVER = (
    ".filter-item.dropdown:not(.filter_item_icon, .filter_item_single)"
    ":is(:focus-within, :hover)"
)

VAR = re.compile(r"var\(--([\w-]+)\)")
COLOR_MIX = re.compile(
    r"color-mix\(in srgb, var\(--([\w-]+)\) (\d+)%, var\(--([\w-]+)\)\)"
)


def rule_property(css, selector, prop):
    block = re.search(re.escape(selector) + r"\s*\{(.*?)\}", css, re.DOTALL)
    assert block, f"no rule for {selector}"
    return re.search(rf"{prop}:\s*([^;]+);", block.group(1)).group(1)


def resolve(value, palette):
    if match := VAR.fullmatch(value):
        return palette[match.group(1)]
    if match := COLOR_MIX.fullmatch(value):
        top, percent, bottom = match.groups()
        return mix(palette[bottom], palette[top], int(percent) / 100)
    raise ValueError(value)


def test_dropdown_hover_rule_appended():
    out = convert(FIXTURE)
    assert (
        rule_property(out, DROPDOWN_HOVER, "background")
        == "color-mix(in srgb, var(--violet) 30%, var(--bg-0))"
    )
    assert rule_property(out, DROPDOWN_HOVER, "color") == "var(--fg-1)"


@pytest.mark.parametrize("variant", ["light", "dark"])
def test_dropdown_hover_text_is_readable(variant):
    out = convert(FIXTURE)
    palette = PALETTES[variant]
    background = resolve(rule_property(out, DROPDOWN_HOVER, "background"), palette)
    text = resolve(rule_property(out, DROPDOWN_HOVER, "color"), palette)
    assert contrast(text, background) >= 4.5


def test_unverified_dropdown_variables_left_alone():
    out = convert(FIXTURE)
    assert "--dd-hover-bg: var(--violet);" in out
    assert "--dd-hover-color: var(--fg-0);" in out
