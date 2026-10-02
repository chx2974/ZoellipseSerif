"""Mixing proof: Zoellipse Serif runs set inside Zoellipse text at the same size.

python scripts/proof_mix.py --zoellipse ../zoellipse/fonts/variable [--weights 400,700]
    [--size 64] [--italic] [--out mix.png] [--lines "Sans {serif} sans;..."]
Text inside {braces} is set in Zoellipse Serif, the rest in Zoellipse; each line is
rendered at every weight, unhinted (FreeType + HarfBuzz), with x-height and cap
guides from Zoellipse Serif's OS/2 table.
"""
import argparse
import re
from pathlib import Path

import freetype
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "specimen" / "proofs"
LINES = ["Hamburg {Hamburg} xxx {xxx} HHH {HHH}",
         "The {quick brown} fox {jumps} over the {lazy} dog",
         "Sans and {serif} share one {x-height and cap height}."]


def glyphs(path, wght, text, size):
    blob = hb.Blob.from_file_path(str(path))
    font = hb.Font(hb.Face(blob))
    font.set_variations({"wght": wght})
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, {})
    face = freetype.Face(str(path))
    face.set_var_design_coords((wght,))
    face.set_char_size(size * 64)
    sc = size / face.units_per_EM
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        face.load_glyph(info.codepoint, freetype.FT_LOAD_RENDER | freetype.FT_LOAD_NO_HINTING)
        yield face.glyph, pos.x_advance * sc, pos.x_offset * sc, pos.y_offset * sc


def line(runs, wght, size, guides=()):
    asc, desc = int(size * 1.0), int(size * 0.3)
    width = 40 + sum(adv for path, text in runs for _, adv, _, _ in glyphs(path, wght, text, size))
    img = Image.new("L", (int(width) + 40, asc + desc), 255)
    for h in guides:
        y = asc - round(h * size / 1000)
        ImageDraw.Draw(img).line([(0, y), (img.width, y)], fill=190)
    x = 20.0
    for path, text in runs:
        for g, adv, dx, dy in glyphs(path, wght, text, size):
            bm = g.bitmap
            if bm.width and bm.rows:
                a = Image.frombytes("L", (bm.width, bm.rows), bytes(bm.buffer))
                img.paste(0, (int(x + dx) + g.bitmap_left, asc - g.bitmap_top - int(dy)),
                          a)
            x += adv
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zoellipse", default=str(ROOT.parent / "zoellipse" / "fonts" / "variable"))
    ap.add_argument("--weights", default="400,700")
    ap.add_argument("--size", type=int, default=64)
    ap.add_argument("--italic", action="store_true")
    ap.add_argument("--lines", default=";".join(LINES))
    ap.add_argument("--out", default="mix.png")
    a = ap.parse_args()
    suffix = "-Italic" if a.italic else ""
    sans = Path(a.zoellipse) / f"Zoellipse{suffix}[wght].ttf"
    serif = ROOT / "fonts" / "variable" / f"ZoellipseSerif{suffix}[wght].ttf"
    os2 = TTFont(serif)["OS/2"]
    rows = []
    for text in a.lines.split(";"):
        parts = re.split(r"(\{[^}]*\})", text)
        runs = [(serif, p[1:-1]) if p.startswith("{") else (sans, p) for p in parts if p]
        for w in map(int, a.weights.split(",")):
            rows.append(line(runs, w, a.size, (0, os2.sxHeight, os2.sCapHeight)))
    sheet = Image.new("L", (max(r.width for r in rows), sum(r.height for r in rows)), 255)
    y = 0
    for r in rows:
        sheet.paste(r, (0, y))
        y += r.height
    OUT.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT / a.out)
    print(OUT / a.out)


if __name__ == "__main__":
    main()
