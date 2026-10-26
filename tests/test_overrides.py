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

VAR = re.compile(r"var\(--([\w-]+)\)")
COLOR_MIX = re.compile(
    r"color-mix\(in srgb, var\(--([\w-]+)\) (\d+)%, var\(--([\w-]+)\)\)"
)


def declared(css, name):
    return re.search(rf"--{name}:\s*([^;]+);", css).group(1)


def resolve(value, palette):
    if match := VAR.fullmatch(value):
        return palette[match.group(1)]
    if match := COLOR_MIX.fullmatch(value):
        top, percent, bottom = match.groups()
        return mix(palette[bottom], palette[top], int(percent) / 100)
    raise ValueError(value)


def test_dropdown_hover_overridden():
    out = convert(FIXTURE)
    assert (
        declared(out, "dd-hover-bg")
        == "color-mix(in srgb, var(--violet) 30%, var(--bg-0))"
    )
    assert declared(out, "dd-hover-color") == "var(--fg-1)"


@pytest.mark.parametrize("variant", ["light", "dark"])
def test_dropdown_hover_text_is_readable(variant):
    out = convert(FIXTURE)
    palette = PALETTES[variant]
    background = resolve(declared(out, "dd-hover-bg"), palette)
    text = resolve(declared(out, "dd-hover-color"), palette)
    assert contrast(text, background) >= 4.5
