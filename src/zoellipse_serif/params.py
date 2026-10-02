"""Zoellipse Serif: every number that makes it differ from Source Serif 4.

Zoellipse Serif is a Modified Version of Source Serif 4 (OFL 1.1, Reserved Font
Name "Source", which this family does not use). The pipeline loads the upstream
UFO masters of the Text optical size unchanged and applies the transforms below
in code. Units are Source Serif's (UPM 1000).
"""
from pathlib import Path

FAMILY = "Zoellipse Serif"
FILE = "ZoellipseSerif"                 # file-name / PostScript-name prefix
VERSION = (1, 0)
VENDOR = "NONE"

ROOT = Path(__file__).resolve().parents[2]
UPSTREAM = ROOT / "upstream" / "source-serif"
SLOPES = {False: "Roman", True: "Italic"}
# Text optical size masters (opsz 20): ExtraLight, Regular, Black at design 0 / 394 / 1000.
MASTERS = {False: ["Masters/text/master_0/SourceSerif_0.ufo",
                   "Masters/text/master_1/SourceSerif_1.ufo",
                   "Masters/text/master_2/SourceSerif_2.ufo"],
           True: ["Masters/text/master_0/SourceSerif-Italic_0.ufo",
                  "Masters/text/master_1/SourceSerif-Italic_1.ufo",
                  "Masters/text/master_2/SourceSerif-Italic_2.ufo"]}
MASTER_DESIGN = (0, 394, 1000)
MASTER_STYLE = ("ExtraLight", "Regular", "Black")

UPM = 1000
CAP = 670                            # Source Serif Text Regular cap height
XH = 475                             # Source Serif Text Regular x-height (71% of cap)

# Sizes match Zoellipse at the same font size: everything scales by SCALE so the
# cap height becomes Zoellipse's 0.723 em, then lowercase heights are raised so
# the x-height becomes Zoellipse's 0.528 em (factor XH_RAISE, applied piecewise:
# 0..x-height stretches, x-height..cap compresses, ascenders and descenders stay).
# Source Serif's heights vary a little with weight; each master keeps its own
# x-height and cap height times the same factors.
ZOELLIPSE_CAP = 723
ZOELLIPSE_XH = 528
SCALE = ZOELLIPSE_CAP / CAP          # 1.0791
XH_RAISE = ZOELLIPSE_XH / (XH * SCALE)   # 1.030
XH_PUNCT = ("hyphen", "softhyphen", "endash", "emdash", "guillemotleft", "guillemotright",
            "guilsinglleft", "guilsinglright", "colon", "semicolon", "periodcentered", "bullet")

# Weight matching: n stem of Zoellipse (per 1000 units) at each named weight,
# measured from the Zoellipse build on 2026-10-02 (upright and italic). Each
# Zoellipse Serif weight is put where its (scaled) n stem equals these.
ZOELLIPSE_STEMS = {
    False: {200: 62.1, 300: 77.5, 400: 92.0, 500: 106.6, 600: 121.3, 700: 145.7, 800: 170.1, 900: 194.5},
    True: {200: 59.4, 300: 75.2, 400: 90.1, 500: 104.9, 600: 119.7, 700: 144.4, 800: 169.2, 900: 193.9},
}
DEFAULT_WGHT = 400

# Superellipse feel: curves running from a horizontal to a vertical tangent get
# longer handles, as if an ellipse (n = 2) became a superellipse of exponent N.
SUPER_N = 2.4
SUPER_MIN_SPAN = 30                  # skip quarter curves smaller than this (serif brackets, joins)

LINE_ASC, LINE_DESC = 963, -237      # hhea/typo: 1.2 em, as Zoellipse (1925/-475 per 2000)

COPYRIGHT = ("Copyright 2026 The Zoellipse Serif Project Authors (https://github.com/chx2974/ZoellipseSerif); "
             "Copyright 2014-2023 Adobe (http://www.adobe.com/), with Reserved Font Name 'Source'")
DESIGNER = "Charlie Champanhet; Source Serif: Frank Grießhammer"
DESCRIPTION = ("Zoellipse Serif is a Modified Version of Source Serif 4 with subtly superelliptic "
               "curves, sized and weighted to mix with Zoellipse.")
LICENSE = ("This Font Software is licensed under the SIL Open Font License, Version 1.1. "
           "This license is available with a FAQ at: https://openfontlicense.org")
LICENSE_URL = "https://openfontlicense.org"

