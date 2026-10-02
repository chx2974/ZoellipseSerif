"""Raise the lowercase x-height by P.XH_RAISE (to Zoellipse's 0.528 em; runs after scale.py).

Heights are remapped piecewise, per master (Source Serif's x-height grows a
little with weight): 0..x-height scales up, x-height..ascender is compressed so
ascenders keep their height, descenders do not move. Contours lying wholly
above the x-height (i/j dots) move up rigidly instead, accent components in
lowercase composites follow their base anchor, and oldstyle figures (.osf,
.tosf), which are drawn on the x-height, are treated as lowercase.
Punctuation placed on the x-height (hyphen, dashes, guillemets, colon top dot
...) moves rigidly, contour by contour, by the mapping at its centre; contours
sitting on the baseline stay. Italic outlines are remapped vertically as drawn,
keeping Adobe's horizontal/vertical extrema (stems lean ~0.3 degree less);
rigid moves follow the italic angle.
"""
import math
import unicodedata

from . import params as P

SKIP_SUFFIXES = ("sups", "subs", "sinf", "numr", "dnom", "superior", "inferior", "sc")
OLDSTYLE = (".osf", ".tosf")


class _Map:
    def __init__(self, ufo):
        self.lo = ufo.info.xHeight
        self.hi = round(self.lo * P.XH_RAISE)
        self.top = ufo.info.ascender
        self.slant = math.tan(math.radians(-(ufo.info.italicAngle or 0)))

    def y(self, y):
        if y <= 0:
            return y
        if y <= self.lo:
            return y * self.hi / self.lo
        if y <= self.top:
            return self.hi + (y - self.lo) * (self.top - self.hi) / (self.top - self.lo)
        return y

    def point(self, p):
        p.y = round(self.y(p.y))

    def move(self, p, dy):
        p.x, p.y = round(p.x + self.slant * dy), p.y + dy


def is_lowercase(ufo, name):
    base, _, suffix = name.partition(".")
    if any(s in suffix.split(".") for s in SKIP_SUFFIXES):
        return False
    if name.endswith(OLDSTYLE):
        return True
    for part in base.split("_"):
        g = ufo[part] if part in ufo else None
        if g is None or not g.unicodes:
            return False
        if unicodedata.category(chr(g.unicodes[0])) != "Ll":
            return False
    return True


def transform(ufo):
    m = _Map(ufo)
    names = [g.name for g in ufo if is_lowercase(ufo, g.name)]
    deltas = {}                     # (glyph, anchor name) -> dy, for composites
    for name in names:
        g = ufo[name]
        for c in g.contours:
            if min(p.y for p in c.points) > m.lo + 20:          # dot: move rigidly
                for p in c.points:
                    m.move(p, m.hi - m.lo)
            else:
                for p in c.points:
                    m.point(p)
        for a in g.anchors:
            new = round(m.y(a.y))
            deltas[(name, a.name)] = new - a.y
            a.x, a.y = round(a.x + m.slant * (new - a.y)), new
    for name in names:
        g = ufo[name]
        if not g.components:
            continue
        base = g.components[0].baseGlyph
        for comp in g.components[1:]:
            mark = ufo[comp.baseGlyph] if comp.baseGlyph in ufo else None
            attach = [a.name[1:] for a in (mark.anchors if mark else []) if a.name.startswith("_")]
            dy = next((deltas[(base, n)] for n in attach if (base, n) in deltas), None)
            if dy is None:
                continue
            t = comp.transformation
            comp.transformation = (t[0], t[1], t[2], t[3], round(t[4] + m.slant * dy), t[5] + dy)
    for name in P.XH_PUNCT:
        if name in ufo:
            for c in ufo[name].contours:
                ys = [p.y for p in c.points]
                if min(ys) <= 20:
                    continue
                cy = (min(ys) + max(ys)) / 2
                dy = round(m.y(cy) - cy)
                for p in c.points:
                    m.move(p, dy)
    ufo.info.xHeight = m.hi
    return names
