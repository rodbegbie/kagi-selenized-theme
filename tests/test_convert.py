import re
from pathlib import Path

import pytest

from build_theme import NAME_MAP, PALETTES, convert

ROOT = Path(__file__).parent.parent
REFERENCES = {
    "github": ROOT / "reference/github/custom.css",
    "gist": ROOT / "reference/gist/kagi-catppuccin-mocha.css",
}

FIXTURE = """\
:root {
  --rosewater: #dc8a78;
  --text: #4c4f69;
  --crust: #dce0e8;
  --color-scheme: light;
  --link: var(--blue);
  --app-bg-opac: rgba(30, 30, 46, 0);
}

.theme_moon_dark {
  --rosewater: #f5e0dc;
  --text: #cdd6f4;
  --crust: #11111b;
  --app-bg: var(--base);
}

@media (prefers-color-scheme: dark) {
  .theme_moon_dark_conditional {
    --rosewater: #f5e0dc;
    --text: #cdd6f4;
    --crust: #11111b;
    --app-bg: var(--base);
  }
}

header {
  background: var(--crust);
}
"""

SCOPE = re.compile(r"(:root|\.theme_moon_dark(?:_conditional)?)\s*\{(.*?)\}", re.DOTALL)
PALETTE_DECL = re.compile(r"--([\w-]+):\s*(#[0-9a-f]{6});")
DECL = re.compile(r"^\s*(--[\w-]+)\s*:", re.MULTILINE)
VAR_REF = re.compile(r"var\((--[\w-]+)")
RENAMED = [old for old, new in NAME_MAP.items() if old != new]
OLD_NAME = re.compile(r"--(" + "|".join(RENAMED) + r")(?![\w-])")
LITERAL = re.compile(r"#[0-9a-fA-F]{3,8}\b|rgba?\([^)]*\)")

ALLOWED_LITERALS = {
    "rgba(0, 0, 0,": "black shadows are theme-neutral",
    "rgba(255, 255, 255,": "white overlay on the sidebar is theme-neutral",
}


def palettes_by_scope(css):
    return {
        selector: dict(PALETTE_DECL.findall(body))
        for selector, body in SCOPE.findall(css)
    }


def test_references_rewritten():
    out = convert(FIXTURE)
    assert "var(--bg-1)" in out
    assert "var(--bg-0)" in out
    assert not OLD_NAME.search(out)


def test_scopes_get_their_variant():
    scopes = palettes_by_scope(convert(FIXTURE))
    assert scopes[":root"]["bg-0"] == PALETTES["light"]["bg-0"] == "#fbf3db"
    for selector in (".theme_moon_dark", ".theme_moon_dark_conditional"):
        assert scopes[selector]["bg-0"] == PALETTES["dark"]["bg-0"] == "#103c48"
        assert scopes[selector] == PALETTES["dark"]
    assert scopes[":root"] == PALETTES["light"]


def test_non_palette_declarations_preserved():
    out = convert(FIXTURE)
    assert "--color-scheme: light;" in out
    assert "--link: var(--blue);" in out


def test_base_alpha_literal_follows_scope():
    out = convert(FIXTURE)
    assert "--app-bg-opac: color-mix(in srgb, var(--bg-0) 0%, transparent);" in out


def test_name_collision_fails():
    css = FIXTURE.replace("--link: var(--blue);", "--dim: red;")
    with pytest.raises(ValueError, match="--dim"):
        convert(css)


def test_clock_fill_literal_uses_palette():
    css = FIXTURE + "\ncircle.clock {\n  fill: rgb(150, 120, 120);\n}\n"
    out = convert(css)
    assert "fill: var(--dim);" in out
    assert "rgb(150, 120, 120)" not in out


def test_trailing_newline_in_input_adds_no_blank_lines():
    assert "\n\n\n" not in convert(FIXTURE)


@pytest.mark.parametrize(
    "reference",
    [
        pytest.param(
            path,
            id=name,
            marks=pytest.mark.skipif(
                not path.exists(), reason=f"{name} reference not cloned"
            ),
        )
        for name, path in REFERENCES.items()
    ],
)
def test_real_reference(reference):
    source = reference.read_text(encoding="utf-8")
    out = convert(source)

    assert not OLD_NAME.search(out)

    def unresolved(css):
        return set(VAR_REF.findall(css)) - set(DECL.findall(css))

    mapped = {f"--{k}": f"--{v}" for k, v in NAME_MAP.items()}
    assert unresolved(out) == {mapped.get(n, n) for n in unresolved(source)}

    def non_palette_count(css, names):
        return sum(1 for n in DECL.findall(css) if n[2:] not in names)

    assert non_palette_count(out, PALETTES["light"]) == non_palette_count(
        source, NAME_MAP
    )

    for line in out.splitlines():
        if PALETTE_DECL.search(line) or not LITERAL.search(line):
            continue
        assert any(allowed in line for allowed in ALLOWED_LITERALS), line
