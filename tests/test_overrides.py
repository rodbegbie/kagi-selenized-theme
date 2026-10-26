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
    blocks = re.findall(
        re.escape(selector) + r"\s*(?:,[^{}]*)?\{(.*?)\}", css, re.DOTALL
    )
    assert blocks, f"no rule for {selector}"
    return re.search(rf"(?<![\w-]){prop}:\s*([^;]+);", blocks[-1]).group(1)


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


TOGGLE_BAR = ".k_ui_toggle_switch input:checked ~ .k_ui_toggle_switch_bar"
TOGGLE_KNOB = ".k_ui_toggle_switch input:checked ~ .k_ui_toggle_switch_bar::after"


def test_enabled_toggle_rules_appended():
    out = convert(FIXTURE)
    assert rule_property(out, TOGGLE_BAR, "background") == "var(--br-green)"
    assert rule_property(out, TOGGLE_BAR, "border-color") == "var(--br-green)"
    assert rule_property(out, TOGGLE_KNOB, "background-color") == "var(--bg-0)"


@pytest.mark.parametrize("variant", ["light", "dark"])
@pytest.mark.parametrize("surface", ["bg-0", "bg-1"])
def test_enabled_toggle_is_visible(variant, surface):
    out = convert(FIXTURE)
    palette = PALETTES[variant]
    bar = resolve(rule_property(out, TOGGLE_BAR, "background"), palette)
    knob = resolve(rule_property(out, TOGGLE_KNOB, "background-color"), palette)
    assert contrast(bar, palette[surface]) >= 3
    assert contrast(knob, bar) >= 3


def test_unverified_dropdown_variables_left_alone():
    out = convert(FIXTURE)
    assert "--dd-hover-bg: var(--violet);" in out
    assert "--dd-hover-color: var(--fg-1);" in out


RANK = "._0_d_info_ranking.k_ui_btn_group"
RANK_BAR = RANK
RANK_BUTTON = f"{RANK} .k_ui_btn"
RANK_BAN_BUTTON = f"{RANK} #domain_rank_ban + .k_ui_btn"
RANK_SELECTED = f"{RANK} input:checked + .k_ui_btn"
RANK_BAN_SELECTED = f"{RANK} #domain_rank_ban:checked + .k_ui_btn"
RANK_BOOST_SELECTED = f"{RANK} #domain_rank_boost:checked + .k_ui_btn"
RANK_NOTE = ".ranking-note"


def test_domain_popup_rules_appended():
    out = convert(FIXTURE)
    assert rule_property(out, RANK_BAR, "background-color") == "var(--bg-2)"
    assert rule_property(out, RANK_BAR, "color") == "var(--fg-1)"
    assert rule_property(out, RANK_BUTTON, "color") == "var(--fg-1)"
    assert rule_property(out, RANK_BAN_BUTTON, "color") == "var(--fg-1)"
    assert rule_property(out, RANK_SELECTED, "background-color") == "var(--fg-1)"
    assert rule_property(out, RANK_SELECTED, "color") == "var(--bg-0)"
    assert rule_property(out, RANK_BAN_SELECTED, "background-color") == "var(--br-red)"
    assert rule_property(out, RANK_BAN_SELECTED, "color") == "var(--bg-0)"
    assert (
        rule_property(out, RANK_BOOST_SELECTED, "background-color") == "var(--br-blue)"
    )
    assert rule_property(out, RANK_BOOST_SELECTED, "color") == "var(--bg-0)"
    assert rule_property(out, RANK_NOTE, "background-color") == "var(--bg-2)"
    assert rule_property(out, RANK_NOTE, "color") == "var(--fg-1)"


@pytest.mark.parametrize("variant", ["light", "dark"])
@pytest.mark.parametrize(
    ("selector", "background_prop"),
    [
        (RANK_BAR, "background-color"),
        (RANK_SELECTED, "background-color"),
        (RANK_BOOST_SELECTED, "background-color"),
        (RANK_NOTE, "background-color"),
    ],
)
def test_domain_popup_text_is_readable(variant, selector, background_prop):
    out = convert(FIXTURE)
    palette = PALETTES[variant]
    background = resolve(rule_property(out, selector, background_prop), palette)
    text = resolve(rule_property(out, selector, "color"), palette)
    assert contrast(text, background) >= 4.5


@pytest.mark.parametrize("variant", ["light", "dark"])
@pytest.mark.parametrize("selector", [RANK_BUTTON, RANK_BAN_BUTTON])
def test_domain_popup_button_text_is_readable_on_bar(variant, selector):
    out = convert(FIXTURE)
    palette = PALETTES[variant]
    bar = resolve(rule_property(out, RANK_BAR, "background-color"), palette)
    text = resolve(rule_property(out, selector, "color"), palette)
    assert contrast(text, bar) >= 4.5


@pytest.mark.parametrize("variant", ["light", "dark"])
def test_domain_popup_block_selected_text_is_legible(variant):
    out = convert(FIXTURE)
    palette = PALETTES[variant]
    background = resolve(
        rule_property(out, RANK_BAN_SELECTED, "background-color"), palette
    )
    text = resolve(rule_property(out, RANK_BAN_SELECTED, "color"), palette)
    assert contrast(text, background) >= 4.0
