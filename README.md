# Zoellipse Serif

Zoellipse Serif is a variable serif font, the companion of Zoellipse. It is a
Modified Version of [Source Serif 4](https://github.com/adobe-fonts/source-serif)
by Frank Grießhammer (Adobe). Version 1.000.

Designer: Charlie Champanhet. License: SIL OFL 1.1. Built in code (Python) from the
unmodified Source Serif 4 UFO masters (Text optical size) in `upstream/source-serif/`
(pinned commit b3980ad).

## What changed compared to Source Serif 4

1. **Curves**: a slight superellipse feel. The handles of quarter curves
   (horizontal to vertical) are lengthened the same way as in Zoellipse
   (superellipse exponent 2.4 instead of an ellipse's 2).
2. **Sized to match Zoellipse**: everything is scaled by 1.079 inside the em so
   the cap height (0.723 em) equals Zoellipse's, then the lowercase is raised 3%
   so the x-height (0.528 em) equals Zoellipse's too. Serif and sans mix at the
   same font size; line height is 1.2 em like Zoellipse.
3. **Weights matched to Zoellipse**: each named weight sits where its n stem
   equals Zoellipse's at that weight (upright to upright, italic to italic).
   All weights match exactly, except Black Italic, which is as heavy as
   Source Serif's heaviest italic allows (a little lighter than Zoellipse
   Black Italic).
4. **Text optical size only**: Source Serif 4's optical size axis (Caption to
   Display) is not included; Zoellipse Serif is the Text design.
5. **Archaic Greek capitals added**: Source Serif has only the lowercase
   forms; Zoellipse Serif adds Ϗ (kai), Ϙ (koppa), Ϛ (stigma), Ϝ (digamma) and
   Ϡ (sampi), built from K, O, F and the lowercase forms, so case mapping works.
6. **Build fixes**: the Greek theta's contours are turned the right way round,
   the italic's ss03 gets a name, a dotted circle (U+25CC) is added, gasp,
   prep and meta tables are added.
7. **Renamed** to Zoellipse Serif. The Reserved Font Name "Source" is not used.

Everything else is Source Serif 4: Latin, Greek and Cyrillic, small caps
(`smcp`, `c2sc`), oldstyle and tabular figures (`onum`, `tnum`), fractions,
superiors and inferiors, stylistic sets, kerning, about 1500 glyphs upright and
1100 italic.

## Fonts

Weight axis `wght` 200-900, default Regular 400. Named instances: ExtraLight 200,
Light 300, Regular 400, Medium 500, SemiBold 600, Bold 700, ExtraBold 800,
Black 900.

- `fonts/variable/ZoellipseSerif[wght].ttf` / `.woff2`
- `fonts/variable/ZoellipseSerif-Italic[wght].ttf` / `.woff2`

The two are linked by the STAT `ital` axis.

## Web usage

```css
@font-face {
  font-family: "Zoellipse Serif";
  src: url("fonts/variable/ZoellipseSerif%5Bwght%5D.woff2") format("woff2"),
       url("fonts/variable/ZoellipseSerif%5Bwght%5D.ttf") format("truetype");
  font-weight: 200 900;
  font-style: normal;
  font-display: swap;
}
@font-face {
  font-family: "Zoellipse Serif";
  src: url("fonts/variable/ZoellipseSerif-Italic%5Bwght%5D.woff2") format("woff2"),
       url("fonts/variable/ZoellipseSerif-Italic%5Bwght%5D.ttf") format("truetype");
  font-weight: 200 900;
  font-style: italic;
  font-display: swap;
}
body { font-family: "Zoellipse Serif", Georgia, serif; }
```

## Pairing with Zoellipse

Zoellipse Serif has the same cap height, x-height and stem weights as Zoellipse,
so the two mix with no size or weight adjustment:

```css
body       { font-family: "Zoellipse", sans-serif; }
blockquote { font-family: "Zoellipse Serif", serif; }
```

## Build

Generated from the unmodified Source Serif 4 UFO masters in
`upstream/source-serif/`. Requirements: Python 3.10+ (`python3`) and `make`;
the first `make` creates a local virtualenv in `.venv/` from
`requirements-dev.txt` (pinned versions).
```
make build     # write sources/ and the variable fonts into fonts/variable/
make check     # check_outlines, check_squircle
make qa        # Font Bakery reports in qa/
make release   # build + check + dist/ (variable + static fonts, zip)
make gfbuild   # rebuild from sources/ with gftools builder (Google Fonts)
make serve     # http://localhost:8004/specimen/
```
`scripts/proof_mix.py` renders Zoellipse text with Zoellipse Serif runs (needs a
Zoellipse build; `--zoellipse DIR`).

## License
SIL Open Font License 1.1. See `OFL.txt`, `AUTHORS.txt`, `CONTRIBUTORS.txt` and
`FONTLOG.txt`. Copyright 2026 The Zoellipse Serif Project Authors; copyright
2014-2023 Adobe, with Reserved Font Name "Source" (Source Serif 4). The new
parts add no Reserved Font Name. "Source" is a trademark of Adobe in the United
States and/or other countries.
