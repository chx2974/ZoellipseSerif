"""Match Zoellipse's stroke weight at every named weight.

Each named weight (user 200..900) is placed at the design location where
Zoellipse Serif's n stem (after scaling) equals Zoellipse's n stem at that weight
(P.ZOELLIPSE_STEMS, upright or italic). Stems interpolate linearly between the
masters, so the location is found piecewise. Source Serif's masters (ExtraLight,
Regular, Black) reach past both ends, so new masters are interpolated at the
ExtraLight, Regular and Black locations and replace them: the variable font's
axis ends and default must be masters. Outlines are exact interpolations,
nothing is redrawn.
"""
import copy

from fontTools.designspaceLib import SourceDescriptor
from fontTools.pens.basePen import BasePen
from fontmake.instantiator import Instantiator

from . import params as P


class _Poly(BasePen):
    def __init__(self, gs):
        super().__init__(gs)
        self.segs, self.cur, self.start = [], None, None

    def _moveTo(self, p):
        self.cur = self.start = p

    def _closePath(self):
        if self.cur != self.start:
            self.segs.append((self.cur, self.start))

    _endPath = _closePath

    def _lineTo(self, p):
        self.segs.append((self.cur, p))
        self.cur = p

    def _curveToOne(self, a, b, c):
        p0 = self.cur
        prev = p0
        for k in range(1, 17):
            t, u = k / 16, 1 - k / 16
            q = (u**3 * p0[0] + 3 * u * u * t * a[0] + 3 * u * t * t * b[0] + t**3 * c[0],
                 u**3 * p0[1] + 3 * u * u * t * a[1] + 3 * u * t * t * b[1] + t**3 * c[1])
            self.segs.append((prev, q))
            prev = q
        self.cur = c


def stem(ufo, slant):
    """Width of the n's left stem at 30% of the x-height (unslanted)."""
    pen = _Poly(ufo)
    ufo["n"].draw(pen)
    y = 0.3 * ufo.info.xHeight
    xs = sorted(x0 + (y - y0) * (x1 - x0) / (y1 - y0) - slant * y
                for (x0, y0), (x1, y1) in pen.segs if (y0 > y) != (y1 > y))
    return xs[1] - xs[0]


def design_for(target, masters):
    """Design location whose interpolated stem equals target (clamped)."""
    if target <= masters[0][1]:
        return masters[0][0]
    for (d0, s0), (d1, s1) in zip(masters, masters[1:]):
        if target <= s1:
            return d0 + (d1 - d0) * (target - s0) / (s1 - s0)
    return masters[-1][0]


def stem_at(d, masters):
    for (d0, s0), (d1, s1) in zip(masters, masters[1:]):
        if d <= d1:
            return s0 + (s1 - s0) * (d - d0) / (d1 - d0)
    return masters[-1][1]


def _complete(new, base, style):
    """Interpolated UFOs carry outlines, anchors, kerning and info only."""
    new.features.text = base.features.text
    new.groups.clear()
    new.groups.update(copy.deepcopy(dict(base.groups)))
    for k, v in base.lib.items():
        new.lib.setdefault(k, copy.deepcopy(v))
    new.lib["public.glyphOrder"] = list(base.lib["public.glyphOrder"])
    new.info.italicAngle = base.info.italicAngle
    new.info.styleName = style
    return new


def match(ds, italic, slant):
    axis = ds.axes[0]
    targets = P.ZOELLIPSE_STEMS[italic]
    masters = sorted((src.location[axis.name], stem(src.font, slant)) for src in ds.sources)
    users = sorted(targets)
    designs = [round(design_for(targets[u], masters), 1) for u in users]
    for inst, d in zip(ds.instances, designs):        # instances are in weight order
        inst.location = {axis.name: d}
    keep = [0, users.index(P.DEFAULT_WGHT), len(users) - 1]   # ExtraLight, Regular, Black
    gen = Instantiator.from_designspace(ds)
    base = next(src.font for src in ds.sources if src.location[axis.name] == axis.default)
    new = []
    for i in keep:
        inst = ds.instances[i]
        ufo = _complete(gen.generate_instance(inst), base, inst.styleName)
        new.append(SourceDescriptor(font=ufo, location={axis.name: designs[i]}, styleName=inst.styleName,
                                    familyName=P.FAMILY))
    ds.sources = new
    axis.minimum, axis.default, axis.maximum = users[0], P.DEFAULT_WGHT, users[-1]
    axis.map = list(zip(users, designs))
    return [(u, d, round(stem_at(d, masters), 1)) for u, d in zip(users, designs)]
