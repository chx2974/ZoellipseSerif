"""Build Zoellipse Serif: Source Serif 4 Text masters -> transforms -> UFOs -> variable TTF/WOFF2.

Usage: python -m zoellipse_serif.build [sources]   (via `make build` / `make sources`)
"""
import shutil
import subprocess
import sys

from fontTools.otlLib.builder import buildStatTable
from fontTools.ttLib import TTFont

import math

from . import fixes, meta, scale, squircle, upstream, weights, xheight
from . import params as P

SOURCES = P.ROOT / "build" / "sources"
OUT = P.ROOT / "fonts" / "variable"
REPO_SOURCES = P.ROOT / "sources"           # commit-ready copy (UFOs + designspaces)

WEIGHTS = upstream.WEIGHTS                   # user 200..900


def make_sources(italic):
    ds = upstream.load(italic)
    for src in ds.sources:
        ufo = src.font
        rev = fixes.fix_directions(ufo)
        nq = squircle.transform(ufo)
        scale.transform(ufo)
        nl = len(xheight.transform(ufo))
        print(f"  {ufo.info.styleName}: {nq} quarter curves squared, scaled {P.SCALE:.4f}, "
              f"{nl} lowercase glyphs raised to x-height {ufo.info.xHeight}, reversed {rev}")
    slant = math.tan(math.radians(-(ds.sources[0].font.info.italicAngle or 0)))
    print("  weights (user, design, stem):", weights.match(ds, italic, slant))
    for src in ds.sources:
        fixes.add_dotted_circle(src.font)
        print(f"  {src.styleName}: {fixes.set_categories(src.font)} marks")
    return ds


def save_sources(ds, italic):
    suffix = "-Italic" if italic else ""
    for src in ds.sources:
        ufo = src.font
        meta.font_info(ufo)
        src.filename = f"{P.FILE}-{ufo.info.styleName.replace(' ', '')}.ufo"
        src.path = str(SOURCES / src.filename)
        ufo.save(src.path, overwrite=True)
    meta.designspace(ds)
    path = SOURCES / f"{P.FILE}{suffix}.designspace"
    ds.write(path)
    return path


def add_stat(font, italic):
    """STAT: wght (named weights, Regular elidable, linked to Bold) + ital."""
    wvals = []
    for i, name in enumerate(WEIGHTS):
        d = {"value": 100 * (i + 2), "name": name}
        if name == "Regular":
            d.update(flags=2, linkedValue=700)
        wvals.append(d)
    ital = ({"value": 1, "name": "Italic"} if italic else
            {"value": 0, "name": "Roman", "flags": 2, "linkedValue": 1})
    buildStatTable(font, [{"tag": "wght", "name": "Weight", "values": wvals},
                          {"tag": "ital", "name": "Italic", "values": [ital]}],
                   elidedFallbackName="Regular")


def finish(ttf, italic):
    font = TTFont(ttf)
    fixes.unhinted_tables(font)
    add_stat(font, italic)
    name = font["name"]
    name.names = [n for n in name.names if n.platformID != 1]
    name.setName(P.FILE + ("Italic" if italic else ""), 25, 3, 1, 0x409)
    font.save(ttf)
    font.flavor = "woff2"
    font.save(ttf.with_suffix(".woff2"))
    print("wrote", ttf.name, "and", ttf.with_suffix(".woff2").name)


def build(ds_path, italic):
    ttf = OUT / f"{P.FILE}{'-Italic' if italic else ''}[wght].ttf"
    cmd = [sys.executable, "-m", "fontmake", "-m", str(ds_path), "-o", "variable",
           "--output-path", str(ttf), "--flatten-components", "--filter", "DecomposeTransformedComponentsFilter"]
    subprocess.run(cmd, check=True)
    finish(ttf, italic)


def export_sources():
    REPO_SOURCES.mkdir(exist_ok=True)
    for old in list(REPO_SOURCES.glob("*.ufo")) + list(REPO_SOURCES.glob("*.designspace")):
        shutil.rmtree(old) if old.is_dir() else old.unlink()
    for src in sorted(SOURCES.iterdir()):
        if src.suffix == ".ufo":
            shutil.copytree(src, REPO_SOURCES / src.name)
        elif src.suffix == ".designspace":
            shutil.copy2(src, REPO_SOURCES / src.name)
    print("exported sources to", REPO_SOURCES)


def main():
    shutil.rmtree(SOURCES, ignore_errors=True)
    SOURCES.mkdir(parents=True)
    dss = {it: make_sources(it) for it in (False, True)}
    scale.win_metrics([src.font for ds in dss.values() for src in ds.sources])   # one value per family
    paths = {it: save_sources(ds, it) for it, ds in dss.items()}
    if "sources" not in sys.argv[1:]:
        OUT.mkdir(parents=True, exist_ok=True)
        for it, path in paths.items():
            build(path, it)
    export_sources()


if __name__ == "__main__":
    main()
