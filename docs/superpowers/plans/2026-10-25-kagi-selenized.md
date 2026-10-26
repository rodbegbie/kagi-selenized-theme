# Kagi Selenized Theme Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development (recommended) or
> superpowers:executing-plans to implement this plan task-by-task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate `kagi-selenized.css`, a Selenized Light and Dark Kagi
theme, by converting the jcrabapple Catppuccin gist.

**Architecture:** A small Python module holds the canonical Selenized
palettes and a Catppuccin-to-Selenized name map. `convert()` replaces the
palette definitions in each scope (light `:root`, dark
`.theme_moon_dark`, dark `prefers-color-scheme` twin) and rewrites every
`var(--old)` reference. Tests pin the palette values, the map, and the
output invariants.

**Tech Stack:** Python 3.13, uv, pytest, ruff.

**Spec:** `docs/superpowers/specs/2026-10-25-kagi-selenized-design.md`

## Global Constraints

- Python 3.13 or later, managed with uv, formatted with ruff, tested with
  pytest.
- Palette values are Jan Warchol's canonical sRGB hex from
  `the-values.md` (Selenized light and dark only).
- New palette names: `--bg-0`, `--bg-1`, `--bg-2`, `--dim`, `--fg-0`,
  `--fg-1`, `--red`, `--orange`, `--yellow`, `--green`, `--cyan`,
  `--blue`, `--violet`, `--magenta`, `--br-red`, `--br-orange`,
  `--br-yellow`, `--br-green`, `--br-cyan`, `--br-blue`, `--br-violet`,
  `--br-magenta`, plus interpolated `--grey-1` to `--grey-4`.
- The reference is untrusted downloaded data: it lives in its own
  directory (`reference/`), is never committed, and Python that reads it
  runs with `-I`.
- No code comments unless essential.
- Branch is `feature/selenized-theme`. Check with
  `git branch --show-current` before each commit.

## Review Focus

- Hard-coded colours outside the palette (for example
  `rgba(30, 30, 46, 0)` in `:root`) stay Catppuccin-tinted unless the
  converter handles them. Expect: none left.
- The two dark scopes (`.theme_moon_dark` and the media-query class) must
  end up with identical palettes. Expect: they do.
- A new palette name may collide with a variable Kagi's own block already
  defines. Expect: conversion fails loudly rather than overwriting.
- Text legibility: `fg-0` on `bg-0` and `bg-1` in both variants. Expect:
  at least 4.5:1.
- A `var(--x)` left pointing at a name that no longer exists renders as
  nothing in the browser. Expect: every reference resolves.

---

### Task 1: Palette module

**Files:**

- Create: `pyproject.toml`, `.gitignore` (ignores `reference/`,
  `.venv/`, `__pycache__/`)
- Create: `build_theme.py`
- Test: `tests/test_palette.py`

**Interfaces:**

- Produces: `PALETTES: dict[str, dict[str, str]]` keyed `"light"` and
  `"dark"`, mapping a palette name without `--` (for example `"bg-0"`) to
  a lowercase hex string with `#`. Includes the `grey-1` to `grey-4`
  entries.
- Produces: `mix(a: str, b: str, t: float) -> str`, linear sRGB
  interpolation per channel, rounding with `int(x + 0.5)`, returning
  lowercase `#rrggbb`.
- Produces: `NAME_MAP: dict[str, str]` from each of the 26 Catppuccin
  names to a Selenized palette name.
- Produces: `contrast(a: str, b: str) -> float`, WCAG contrast ratio.

- [ ] **Step 1: Scaffold**

`uv init --no-workspace --python 3.13` in the project directory, then
`uv add --dev pytest ruff`. Keep `build_theme.py` as a single module at
the project root.

- [ ] **Step 2: Write the failing tests in `tests/test_palette.py`**

- `test_canonical_values`: light `bg-0 == "#fbf3db"`, `red == "#d2212d"`,
  `br-violet == "#825dc0"`; dark `bg-0 == "#103c48"`,
  `violet == "#af88eb"`, `br-cyan == "#53d6c7"`.
- `test_mix_midpoint`: `mix("#000000", "#ffffff", 0.5) == "#808080"` and
  `mix("#103c48", "#103c48", 0.3) == "#103c48"`.
- `test_greys_are_interpolated`: in both variants,
  `grey-1 == mix(bg-2, dim, 1/3)`, `grey-2 == mix(bg-2, dim, 2/3)`,
  `grey-3 == mix(dim, fg-0, 1/3)`, `grey-4 == mix(dim, fg-0, 2/3)`.
- `test_name_map_complete`: keys are exactly the 26 Catppuccin names
  (`rosewater flamingo pink mauve red maroon peach yellow green teal sky
  sapphire blue lavender text subtext1 subtext0 overlay2 overlay1
  overlay0 surface2 surface1 surface0 base mantle crust`), and every
  value is a key of both palettes.
- `test_name_map_values`: `base -> bg-0`, `mantle` and `crust -> bg-1`,
  `surface0 -> bg-2`, `surface1 -> grey-1`, `surface2 -> grey-2`,
  `overlay0 -> dim`, `overlay1` and `subtext0 -> grey-3`, `overlay2` and
  `subtext1 -> grey-4`, `text -> fg-0`, `pink` and `flamingo -> magenta`,
  `rosewater` and `peach -> orange`, `lavender` and `mauve -> violet`,
  `sapphire`, `teal` and `sky -> cyan`, `maroon -> br-red`, and `red`,
  `green`, `yellow`, `blue` map to themselves.
- `test_text_contrast`: `contrast(fg-0, bg-0)` and `contrast(fg-0, bg-1)`
  are at least 4.5 in both variants.

- [ ] **Step 3: Run tests, verify they fail**

Run: `uv run pytest tests/test_palette.py -v`
Expected: FAIL (module has no `PALETTES`).

- [ ] **Step 4: Implement in `build_theme.py`**

Hard-code the 22 canonical hex values per variant from the spec source,
then derive the four greys with `mix`.

- [ ] **Step 5: Run tests, verify they pass**

Run: `uv run pytest tests/test_palette.py -v`
Expected: all PASS. If `test_text_contrast` fails, stop and report the
ratio to Rod; do not alter the mapping.

- [ ] **Step 6: Lint and commit**

```bash
uv run ruff format . && uv run ruff check .
git branch --show-current
git add pyproject.toml uv.lock .gitignore build_theme.py tests
git commit -m "Add Selenized palettes and Catppuccin name map"
```

### Task 2: Converter

**Files:**

- Modify: `build_theme.py`
- Test: `tests/test_convert.py`
- Create: `reference/gist/` (git clone, untracked)

**Interfaces:**

- Consumes: `PALETTES`, `NAME_MAP`, from Task 1.
- Produces: `convert(css: str) -> str`.
- Produces: `main(src: Path, dst: Path) -> None`, reading `src`,
  writing `convert(...)` to `dst`.

Scopes: the first `:root` rule is light. Rules whose selector is
`.theme_moon_dark` or `.theme_moon_dark_conditional` (inside
`@media (prefers-color-scheme: dark)`) are dark. In each scope, the run
of Catppuccin palette declarations (`--rosewater` through `--crust`,
hex values) is replaced by that variant's full Selenized palette. Every
`var(--name)` where `name` is in `NAME_MAP` becomes
`var(--<mapped>)` everywhere in the file.

- [ ] **Step 1: Fetch the reference**

Run: `git clone https://repo.jcrabapple.com/jcrabapple/82208449e52b434a8e695c8124fa3f79.git reference/gist`
Note the commit hash from `git -C reference/gist rev-parse HEAD` for the
handoff. If the clone fails, stop and ask Rod to save the raw file to
`reference/gist/kagi-catppuccin-mocha.css`.

- [ ] **Step 2: Inspect the dark scopes**

Read `reference/gist/*.css` lines 237-326. Confirm both dark scopes
define the Catppuccin palette and note any other declarations in them.
If a dark scope has non-palette hard-coded colours, list them for the
converter's literal handling in Step 4.

- [ ] **Step 3: Write the failing tests in `tests/test_convert.py`**

Use a small inline CSS fixture with the three scopes, three palette
names, one Kagi variable (`--link: var(--blue)`) and one shared rule
(`header { background: var(--crust) }`).

- `test_references_rewritten`: output contains `var(--bg-1)` and no
  `--crust`.
- `test_scopes_get_their_variant`: the `:root` scope contains
  `--bg-0: #fbf3db`; both dark scopes contain `--bg-0: #103c48`.
- `test_dark_scopes_identical_palettes`: the palette declarations in the
  two dark scopes are equal.
- `test_name_collision_fails`: a fixture where `:root` also declares
  `--dim: red` outside the palette run raises `ValueError` whose message
  names `--dim`.
- `test_real_reference` (skipped if `reference/gist` is missing): on the
  real file, (a) no `NAME_MAP` key appears as `--key`; (b) every
  `var(--x)` resolves to a declaration in the same file; (c) the number
  of non-palette declarations equals the reference's; (d) no hex colour
  or `rgb(a)` literal remains outside palette declarations except the
  allowlist the implementer records in the test with a reason each.

- [ ] **Step 4: Run tests, verify they fail**

Run: `uv run pytest tests/test_convert.py -v`
Expected: FAIL (`convert` not defined).

- [ ] **Step 5: Implement `convert` and `main`**

Regex-based rewrite is enough; the file is flat CSS. Raise `ValueError`
on name collisions. Map any hard-coded Catppuccin colour literals found
in Step 2 or by test (d) to palette `var()` references or per-scope
Selenized values.

- [ ] **Step 6: Run tests, verify they pass**

Run: `uv run pytest -v`
Expected: all PASS.

- [ ] **Step 7: Generate and commit**

```bash
uv run python -I -c "import pathlib, build_theme as b; b.main(pathlib.Path('reference/gist/kagi-catppuccin-mocha.css'), pathlib.Path('kagi-selenized.css'))"
git branch --show-current
git add build_theme.py tests kagi-selenized.css
git commit -m "Convert reference theme to Selenized"
```

### Task 3: Live check in Kagi

**Files:** none changed unless the check finds defects.

Pasting into Kagi changes Rod's account settings, so ask Rod first.

- [ ] **Step 1: Ask Rod**

Get an explicit yes before touching Kagi's Appearance settings. If no,
stop here and hand over the file.

- [ ] **Step 2: Apply and screenshot**

Paste `kagi-selenized.css` into Kagi's custom CSS field. Check the
search results page, the Assistant chat page and the settings page, in
light and dark (toggle via the OS setting or Chrome's rendering
emulation). Capture screenshots.

- [ ] **Step 3: Fix and regenerate**

For any unreadable or off-palette element, adjust `NAME_MAP` or the
converter, re-run Task 2 Step 7's generation, re-test, re-check, and
commit. Report each change to Rod.
