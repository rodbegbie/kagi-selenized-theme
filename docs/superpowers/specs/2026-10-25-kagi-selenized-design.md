# Kagi Selenized theme: design

## Intent

A Kagi custom-CSS theme using the Selenized palette, in the style of
the jcrabapple Catppuccin gist
(`repo.jcrabapple.com/jcrabapple/82208449e52b434a8e695c8124fa3f79`).
Selenized Light and Selenized Dark switch with the system
`prefers-color-scheme`, as the gist does.

## Goals

- One CSS file, pasteable into Kagi's custom CSS setting.
- Same coverage as the reference: palette block, Kagi variable
  mappings, then shared rules.
- Honest palette names, so the file stays editable.

## Non-goals

- Selenized Black and Selenized White.
- Changes beyond colour. The gist's font (Poppins), chat bubble radius
  and layout tweaks carry over unchanged.

## Reference structure

- Lines 1-235: `:root` holds the light palette (Catppuccin Latte) and
  about 200 Kagi variables pointed at it.
- Lines 237-326: `.theme_moon_dark` and a `prefers-color-scheme: dark`
  twin override the palette for dark (Mocha).
- Lines 328-871: shared rules written against the palette names.

## Approaches considered

1. Keep Catppuccin variable names, swap values. Smallest diff, but the
   names mislead (`--mauve` holding violet).
2. Rename to Selenized terms and rewrite every reference with a mapping
   table. Larger diff, but mechanical and verifiable. **Chosen.**
3. Selenized palette plus an alias layer for the old names. Two
   vocabularies in one file.

## Design

Palette names: `--bg-0`, `--bg-1`, `--bg-2`, `--dim`, `--fg-0`, `--fg-1`,
accents `--red`, `--orange`, `--yellow`, `--green`, `--cyan`, `--blue`,
`--violet`, `--magenta`, and `--br-*` bright variants.

A script applies a Catppuccin-to-Selenized mapping table to the reference
file. Values are Jan Warchol's canonical sRGB values from
`the-values.md` in the selenized repo.

### Mapping (builder's calls, agreed at the design stage)

| Catppuccin | Selenized |
| --- | --- |
| base | bg-0 |
| mantle, crust | bg-1 |
| surface0 | bg-2 |
| surface1, surface2, overlays, subtexts | interpolated greys between bg-2, dim and fg-0 |
| text | fg-0 (fg-1 for emphasis) |
| pink, flamingo | magenta |
| rosewater, peach | orange |
| lavender, mauve | violet |
| sapphire, teal, sky | cyan |
| maroon | br-red |

In dark, Selenized `bg-0` is already the darkest shade, so panels and
the header sit one step lighter than the page, unlike Mocha where
`mantle` and `crust` go darker than `base`.

## Verification

- Variable count matches the reference.
- No Catppuccin names remain (grep).
- Every `var(--x)` resolves to a defined variable.
- Try it live in Kagi through Chrome, light and dark.

## Output

`kagi-selenized.css` in this directory.
