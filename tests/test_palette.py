import pytest

from build_theme import NAME_MAP, PALETTES, contrast, mix

CATPPUCCIN_NAMES = {
    "rosewater",
    "flamingo",
    "pink",
    "mauve",
    "red",
    "maroon",
    "peach",
    "yellow",
    "green",
    "teal",
    "sky",
    "sapphire",
    "blue",
    "lavender",
    "text",
    "subtext1",
    "subtext0",
    "overlay2",
    "overlay1",
    "overlay0",
    "surface2",
    "surface1",
    "surface0",
    "base",
    "mantle",
    "crust",
}


def test_canonical_values():
    assert PALETTES["light"]["bg-0"] == "#fbf3db"
    assert PALETTES["light"]["red"] == "#d2212d"
    assert PALETTES["light"]["br-violet"] == "#825dc0"
    assert PALETTES["dark"]["bg-0"] == "#103c48"
    assert PALETTES["dark"]["violet"] == "#af88eb"
    assert PALETTES["dark"]["br-cyan"] == "#53d6c7"


def test_mix_midpoint():
    assert mix("#000000", "#ffffff", 0.5) == "#808080"
    assert mix("#103c48", "#103c48", 0.3) == "#103c48"


@pytest.mark.parametrize("variant", ["light", "dark"])
def test_greys_are_interpolated(variant):
    p = PALETTES[variant]
    assert p["grey-1"] == mix(p["bg-2"], p["dim"], 1 / 3)
    assert p["grey-2"] == mix(p["bg-2"], p["dim"], 2 / 3)
    assert p["grey-3"] == mix(p["dim"], p["fg-0"], 1 / 3)
    assert p["grey-4"] == mix(p["dim"], p["fg-0"], 2 / 3)


def test_name_map_complete():
    assert set(NAME_MAP) == CATPPUCCIN_NAMES
    for target in NAME_MAP.values():
        assert target in PALETTES["light"]
        assert target in PALETTES["dark"]


def test_name_map_values():
    expected = {
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
        "text": "fg-0",
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
    assert NAME_MAP == expected


@pytest.mark.parametrize("variant", ["light", "dark"])
@pytest.mark.parametrize("background", ["bg-0", "bg-1"])
def test_text_contrast(variant, background):
    p = PALETTES[variant]
    assert contrast(p["fg-0"], p[background]) >= 4.5
