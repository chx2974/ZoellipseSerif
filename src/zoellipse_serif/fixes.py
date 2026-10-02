"""Font-level additions for current Font Bakery / Google Fonts checks."""
import math
import unicodedata

from fontTools.pens.areaPen import AreaPen
from fontTools.pens.recordingPen import RecordingPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.ttLib import newTable
from fontTools.ttLib.tables import ttProgram
from ufoLib2.objects import Component, Glyph


def fix_directions(ufo):
    """Reverse glyphs drawn entirely the wrong way round (upstream theta: outer
    clockwise, counter counter-clockwise). Same fill, consistent direction."""
    fixed = []
    for g in ufo:
        if g.components or not g.contours:
            continue
        pen = AreaPen(ufo)
        g.draw(pen)
        if pen.value < 0:          # UFO/PostScript: outer contours counter-clockwise
            rec = RecordingPen()
            g.draw(ReverseContourPen(rec))
            g.clearContours()
            rec.replay(g.getPen())
            fixed.append(g.name)
    return fixed


def add_dotted_circle(ufo):
    """U+25CC from 12 scaled copies of the period's dot on a circle centred on
    the x-height, with o's mark anchors (plus c's and a's that o lacks) so every
    mark attaches to it (as in Zoellipse)."""
    name, base = "dottedCircle", ufo["o"]
    if name in ufo:
        return None
    pts = [p for c in ufo["period"].contours for p in c.points]
    dcx = (min(p.x for p in pts) + max(p.x for p in pts)) / 2
    dcy = (min(p.y for p in pts) + max(p.y for p in pts)) / 2
    s = min(0.55, 0.11 * ufo.info.xHeight / (max(p.x for p in pts) - min(p.x for p in pts)))  # dots stay apart at Black
    slant = math.tan(math.radians(-(ufo.info.italicAngle or 0)))
    cx, cy = base.width / 2, ufo.info.xHeight / 2
    r = 0.42 * ufo.info.xHeight
    g = Glyph(width=base.width, unicodes=[0x25CC])
    for k in range(12):
        a = math.radians(90 - 30 * k)
        x, y = cx + r * math.cos(a), cy + r * math.sin(a)
        x += slant * (y - cy)
        g.components.append(Component("period", transformation=(s, 0, 0, s, round(x - s * dcx), round(y - s * dcy))))
    for a in base.anchors:
        g.appendAnchor({"name": a.name, "x": a.x, "y": a.y})
    have = {a.name for a in base.anchors}
    for other in ("c", "a"):                    # cedilla (baseLC), ogonek: o has neither
        for a in ufo[other].anchors:
            if a.name not in have and not a.name.startswith("_"):
                have.add(a.name)
                g.appendAnchor({"name": a.name, "x": a.x + (base.width - ufo[other].width) / 2, "y": a.y})
    ufo.layers.defaultLayer.insertGlyph(g, name=name)
    order = ufo.lib.get("public.glyphOrder")
    if order is not None and name not in order:
        order.append(name)
    ufo.lib.setdefault("public.postscriptNames", {})[name] = "uni25CC"
    return name


def set_categories(ufo):
    """GDEF glyph classes (public.openTypeCategories): Adobe's sources have none.
    Glyphs attaching by a "_" anchor or encoded as combining marks are marks,
    everything else is a base, so kern (IgnoreMarks) skips marks."""
    cats = {}
    for g in ufo:
        mark = any(a.name.startswith("_") for a in g.anchors) or any(
            unicodedata.category(chr(u)) == "Mn" for u in g.unicodes)
        cats[g.name] = "mark" if mark else "base"
    ufo.lib["public.openTypeCategories"] = cats
    return sum(v == "mark" for v in cats.values())


def unhinted_tables(font):
    """gasp (smooth at all sizes), prep with smart dropout control, meta (Latn)."""
    gasp = newTable("gasp")
    gasp.version = 1
    gasp.gaspRange = {0xFFFF: 0x000F}
    font["gasp"] = gasp
    prep = newTable("prep")
    prep.program = ttProgram.Program()
    prep.program.fromBytecode(bytes([0xB8, 0x01, 0xFF, 0x85, 0xB0, 0x04, 0x8D]))
    font["prep"] = prep
    meta = newTable("meta")
    meta.data = {"dlng": "Latn", "slng": "Latn"}
    font["meta"] = meta
