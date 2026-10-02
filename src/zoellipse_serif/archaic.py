"""Capitals for the archaic Greek letters Source Serif has only in lowercase.

    U+03CF Ϗ KaiSymbol  = K + the hook of kai (ϗ), hung from the leg's foot serif
    U+03D8 Ϙ Koppa      = O + the stem of koppa (ϙ), widened like a capital stem
    U+03DA Ϛ Stigma     = stigma (ϛ) scaled up to the cap height
    U+03DC Ϝ Digamma    = F (as in most typefaces)
    U+03E0 Ϡ Sampi      = sampi (ϡ) set on the baseline at the cap height

Runs on Source Serif's own masters, before every other transform, so the new
glyphs get the superellipse, scaling and weight matching like the rest. Scaled
glyphs (Ϛ, Ϡ) are taken from a lighter or heavier point of the weight axis so
their strokes keep the master's thickness after scaling: outlines are
interpolated (or slightly extrapolated) between Source Serif's masters, which
keeps every master compatible. Everything is computed in unslanted space.
"""
import math

from . import params as P
from .weights import _Poly

NEW = {"KaiSymbol": 0x03CF, "Koppa": 0x03D8, "Stigma": 0x03DA, "Digamma": 0x03DC, "Sampi": 0x03E0}
# Hook of kai: point indices of the hook inside kai's contour (pinned upstream),
# from the inner junction point round the terminal to the outer junction point.
HOOK = {False: (0, 19, 3), True: (1, 40, 3)}      # contour, first index, last index
TERMINAL_CLEAR = 60          # upright hook terminal ends this far below the baseline
SAMPI_SX = 0.92              # Ϡ horizontal scale (its curved stroke is mostly vertical)
STIGMA_SX = 1.25             # Ϛ horizontal scale; vertically its body goes x-height -> cap height,
STIGMA_TOP, STIGMA_TAIL = 0.6, 1.1   # the flourish above and the tail below scale by these
# Kerning groups to join (kern1 = glyph's right side, kern2 = its left side).
KERN_LIKE = {"KaiSymbol": ("K", "12"), "Koppa": ("O", "12"), "Stigma": ("C", "2"), "Digamma": ("F", "12")}


def _interp(values, d):
    """Piecewise-linear value at design d (extrapolates past the end masters)."""
    D = P.MASTER_DESIGN
    a, b = (0, 1) if d <= D[1] else (1, 2)
    t = (d - D[a]) / (D[b] - D[a])
    return values[a] + t * (values[b] - values[a])


def _solve(values, target):
    """Design location where the piecewise-linear values reach target."""
    D = P.MASTER_DESIGN
    a, b = (0, 1) if target <= values[1] else (1, 2)
    return D[a] + (target - values[a]) * (D[b] - D[a]) / (values[b] - values[a])


def _contours(glyph):
    return [[(p.x, p.y, p.type, p.smooth) for p in c.points] for c in glyph.contours]


def _interp_glyph(glyphs, d):
    out = []
    for cs in zip(*[_contours(g) for g in glyphs]):
        out.append([(_interp([c[i][0] for c in cs], d), _interp([c[i][1] for c in cs], d), cs[0][i][2], cs[0][i][3])
                    for i in range(len(cs[0]))])
    return out, _interp([g.width for g in glyphs], d)


def _draw(glyph, contours):
    pen = glyph.getPointPen()
    for c in contours:
        pen.beginPath()
        for x, y, t, s in c:
            pen.addPoint((round(x), round(y)), segmentType=t, smooth=s)
        pen.endPath()


def _ubounds(contours, sl):
    xs = [x - sl * y for c in contours for x, y, _, _ in c]
    ys = [y for c in contours for _, y, _, _ in c]
    return min(xs), min(ys), max(xs), max(ys)


def _scaled(fonts, name, i, sl, stems, fit):
    """Glyph `name` scaled by fit(contours) -> (sx, ymap), its strokes kept at
    master i's weight by taking it from the design where stem / sx = stem_i."""
    glyphs = [f[name] for f in fonts]
    cs, width = _interp_glyph(glyphs, P.MASTER_DESIGN[i])
    sx, ymap = fit(cs)
    cs, width = _interp_glyph(glyphs, _solve(stems, stems[i] / sx))
    x0, _, x1, _ = _ubounds(cs, sl)
    lsb, rsb = x0, width - x1
    out = [[((x - sl * y) * sx, ymap(y), t, s) for x, y, t, s in c] for c in cs]
    nx0, _, nx1, _ = _ubounds([[(x, y, t, s) for x, y, t, s in c] for c in out], 0)
    k = (1 + sx) / 2                                  # side bearings grow half as much
    dx = lsb * k - nx0
    out = [[(x + dx + sl * y, y, t, s) for x, y, t, s in c] for c in out]
    return out, round(nx1 - nx0 + (lsb + rsb) * k)


def _hook(fonts, i, italic, sl):
    """Kai's hook, hung from K's leg foot serif and stretched to K's width."""
    ci, first, last = HOOK[italic]
    pts = _contours(fonts[i]["kai"])[ci]
    run = list(range(first, len(pts))) + list(range(0, last + 1))
    hook = [pts[j] for j in run]
    hook[0] = (hook[0][0], hook[0][1], "line", False)            # closing segment is a line
    u = [(x - sl * y, y, t, s) for x, y, t, s in hook]
    k = fonts[i]["K"]
    kc = [_contours_of(c) for c in k.contours]
    serif = max((c for c in kc if max(p[1] for p in c) < 100), key=lambda c: min(p[0] - sl * p[1] for p in c))
    right = max(x - sl * y for x, y, _, _ in serif) - 3
    rtop = max(y for x, y, _, _ in serif if x - sl * y >= right)      # serif height at its right end
    left = min(min(x - sl * y for x, y, _, _ in c) for c in kc if max(p[1] for p in c) > 400)
    xj = u[-1][0]                                                  # outer junction point
    xt = min(x for x, _, _, _ in u)                                # terminal
    sx = (right - left) / (xj - xt)
    top = max(y for x, y, _, _ in u if x - xt < 0.15 * (xj - xt))  # terminal top
    bend = max(0, top + TERMINAL_CLEAR)
    drop = max(0, max(u[0][1], u[-1][1]) - (rtop - 12))           # junction inside the serif
    out = []
    for x, y, t, s in u:
        w = min(1, max(0, (xj - x) / (xj - xt)))
        nx, ny = right - (xj - x) * sx, y - drop - max(0, bend - drop) * w
        out.append((nx + sl * ny, ny, t, s))
    return out


def _contours_of(c):
    return [(p.x, p.y, p.type, p.smooth) for p in c.points]


def _koppa_stem(font, sl, ratio):
    stem = _contours(font["koppa"])[0]
    comp = font["koppa"].components[0]
    ox = comp.transformation[4]

    def low(g, dx=0):
        pts = [(p.x - sl * p.y, p.y) for p in g.contours[0].points if p.type]
        return min(pts, key=lambda q: q[1])[0] + dx

    dx = low(font["O"]) - low(font["omicron"], ox)
    us = [(x - sl * y, y, t, s) for x, y, t, s in stem]
    cx = (min(p[0] for p in us) + max(p[0] for p in us)) / 2
    return [(cx + (x - cx) * ratio + ox + dx + sl * y, y, t, s) for x, y, t, s in us]


def _stem(font, name, frac, sl):
    """Width of the first vertical stem of `name` at frac of its height (unslanted)."""
    poly = _Poly(font)
    font[name].draw(poly)
    y = frac * (font.info.capHeight if name.isupper() else font.info.xHeight)
    xs = sorted(x0 + (y - y0) * (x1 - x0) / (y1 - y0) - sl * y
                for (x0, y0), (x1, y1) in poly.segs if (y0 > y) != (y1 > y))
    return xs[1] - xs[0]


def add(fonts, italic):
    """Add the five capitals to Source Serif's three masters (in place)."""
    sl = math.tan(math.radians(-(fonts[0].info.italicAngle or 0)))
    stems = [_stem(f, "n", 0.3, sl) for f in fonts]
    for i, f in enumerate(fonts):
        g = f.newGlyph("Digamma")
        g.width = f["F"].width
        g.getPen().addComponent("F", (1, 0, 0, 1, 0, 0))

        g = f.newGlyph("KaiSymbol")
        g.width = f["K"].width
        g.getPen().addComponent("K", (1, 0, 0, 1, 0, 0))
        _draw(g, [_hook(fonts, i, italic, sl)])

        g = f.newGlyph("Koppa")
        g.width = f["O"].width
        g.getPen().addComponent("O", (1, 0, 0, 1, 0, 0))
        ratio = min(1.25, _stem(f, "H", 0.5, sl) / stems[i])
        _draw(g, [_koppa_stem(f, sl, ratio)])

        top = f["O"].getBounds(f)

        xh, cap = f.info.xHeight, f.info.capHeight

        def fit_stigma(cs, xh=xh, cap=cap):
            """Body (baseline to x-height) up to the cap height; the flourish above
            and the tail below grow less."""
            def ymap(y):
                if y <= 0:
                    return y * STIGMA_TAIL
                if y <= xh:
                    return y * cap / xh
                return cap + (y - xh) * STIGMA_TOP
            return STIGMA_SX, ymap

        def fit_sampi(cs, top=top):
            _, y0, _, y1 = _ubounds(cs, sl)
            sy = (top.yMax - top.yMin) / (y1 - y0)
            return SAMPI_SX, lambda y: y * sy + top.yMin - y0 * sy

        for name, src, fit in (("Stigma", "stigma", fit_stigma), ("Sampi", "sampi", fit_sampi)):
            cs, width = _scaled(fonts, src, i, sl, stems, fit)
            g = f.newGlyph(name)
            g.width = width
            _draw(g, cs)
    for f in fonts:
        for name, cp in NEW.items():
            f[name].unicodes = [cp]
        order = f.lib.setdefault("public.glyphOrder", list(f.keys()))
        order += [n for n in NEW if n not in order]
        f.lib.setdefault("public.postscriptNames", {}).update({n: f"uni{cp:04X}" for n, cp in NEW.items()})
        for name, (like, sides) in KERN_LIKE.items():
            for gname, members in f.groups.items():
                side = gname[len("public.kern"):][:1]
                if gname.startswith("public.kern") and side in sides and like in members and name not in members:
                    members.append(name)
    return list(NEW)
