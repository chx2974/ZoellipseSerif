"""Scale everything by P.SCALE inside the em (UPM stays 1000).

Zoellipse Serif's cap height becomes Zoellipse's (0.670 em x 1.079 = 0.723 em); xheight.py
then raises the lowercase to Zoellipse's x-height. Outlines, component offsets,
anchors, advance widths and the vertical metrics all scale together.
"""
from . import params as P

INFO = ("ascender", "descender", "capHeight", "xHeight",
        "openTypeHheaAscender", "openTypeHheaDescender", "openTypeHheaLineGap",
        "openTypeOS2TypoAscender", "openTypeOS2TypoDescender", "openTypeOS2TypoLineGap",
        "openTypeOS2WinAscent", "openTypeOS2WinDescent",
        "postscriptUnderlinePosition", "postscriptUnderlineThickness",
        "openTypeOS2StrikeoutPosition", "openTypeOS2StrikeoutSize",
        "openTypeOS2SubscriptXSize", "openTypeOS2SubscriptYSize",
        "openTypeOS2SubscriptXOffset", "openTypeOS2SubscriptYOffset",
        "openTypeOS2SuperscriptXSize", "openTypeOS2SuperscriptYSize",
        "openTypeOS2SuperscriptXOffset", "openTypeOS2SuperscriptYOffset")
LISTS = ("postscriptBlueValues", "postscriptOtherBlues", "postscriptFamilyBlues",
         "postscriptFamilyOtherBlues", "postscriptStemSnapH", "postscriptStemSnapV")


def s(v):
    return round(v * P.SCALE)


def transform(ufo):
    for g in ufo:
        for c in g.contours:
            for p in c.points:
                p.x, p.y = s(p.x), s(p.y)
        for comp in g.components:
            t = comp.transformation
            comp.transformation = (t[0], t[1], t[2], t[3], s(t[4]), s(t[5]))
        for a in g.anchors:
            a.x, a.y = s(a.x), s(a.y)
        for gl in g.guidelines or []:
            gl.x, gl.y = s(gl.x or 0), s(gl.y or 0)
        g.width = s(g.width)
    for pair, v in list(ufo.kerning.items()):
        ufo.kerning[pair] = s(v)
    i = ufo.info
    for k in INFO:
        if getattr(i, k) is not None:
            setattr(i, k, s(getattr(i, k)))
    for k in LISTS:
        if getattr(i, k):
            setattr(i, k, [s(v) for v in getattr(i, k)])


def win_metrics(fonts):
    """usWin* covering every glyph of every master of both styles (one value for
    the family; Source Serif's own values scaled would differ between styles)."""
    hi, lo = 0, 0
    for ufo in fonts:
        for g in ufo:
            b = g.getBounds(ufo)
            if b:
                hi, lo = max(hi, b.yMax), min(lo, b.yMin)
    for ufo in fonts:
        ufo.info.openTypeOS2WinAscent = int(hi) + 1
        ufo.info.openTypeOS2WinDescent = int(-lo) + 1
