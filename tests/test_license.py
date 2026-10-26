from pathlib import Path

from build_theme import convert

FIXTURE = ":root {\n  --text: #4c4f69;\n}\n"


def test_output_starts_with_mit_no_attribution_header():
    out = convert(FIXTURE)
    assert out.startswith("/*\n")
    header = out[: out.index("*/") + 2]
    assert "MIT No Attribution" in header
    assert "Copyright (c) 2026 Rod Begbie" in header
    assert "Permission is hereby granted, free of charge" in header
    assert 'THE SOFTWARE IS PROVIDED "AS IS"' in header


def test_header_has_no_attribution_requirement():
    header = convert(FIXTURE)
    assert "provided that the above copyright notice" not in header
    assert "The above copyright notice" not in header


def test_header_precedes_the_rules():
    out = convert(FIXTURE)
    assert out.index("*/") < out.index(":root")


def test_header_contains_license_file_verbatim():
    license_text = (Path(__file__).parent.parent / "LICENSE").read_text()
    assert license_text.strip() in convert(FIXTURE)
