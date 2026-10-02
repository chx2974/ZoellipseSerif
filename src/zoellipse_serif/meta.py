"""Rename Source Serif 4 to Zoellipse Serif in font info and the designspace.

The Reserved Font Name "Source" and Adobe's trademark notice must not appear in
the names of a Modified Version; only the copyright line credits Adobe.
"""
from . import params as P


def ps_name(style):
    return f"{P.FILE}-{style.replace(' ', '') or 'Regular'}"


def font_info(ufo):
    i = ufo.info
    style = i.styleName
    i.familyName = P.FAMILY
    i.styleMapFamilyName = None
    i.styleMapStyleName = None
    i.openTypeNamePreferredFamilyName = None
    i.openTypeNamePreferredSubfamilyName = None
    i.postscriptFontName = ps_name(style)
    i.postscriptFullName = f"{P.FAMILY} {style}"
    i.openTypeNameUniqueID = None
    i.versionMajor, i.versionMinor = P.VERSION
    i.openTypeNameVersion = None
    i.copyright = P.COPYRIGHT
    i.trademark = None
    i.openTypeNameDesigner = P.DESIGNER
    i.openTypeNameDesignerURL = None
    i.openTypeNameManufacturer = None
    i.openTypeNameManufacturerURL = None
    i.openTypeNameDescription = P.DESCRIPTION
    i.openTypeNameLicense = P.LICENSE
    i.openTypeNameLicenseURL = P.LICENSE_URL
    i.openTypeOS2VendorID = P.VENDOR
    i.openTypeOS2Type = []                       # installable
    i.openTypeOS2Panose = None
    i.openTypeOS2Selection = [7]                 # USE_TYPO_METRICS
    i.openTypeHheaAscender = i.openTypeOS2TypoAscender = P.LINE_ASC
    i.openTypeHheaDescender = i.openTypeOS2TypoDescender = P.LINE_DESC
    i.openTypeHheaLineGap = i.openTypeOS2TypoLineGap = 0


def designspace(ds):
    for inst in ds.instances:
        inst.familyName = P.FAMILY
        inst.postScriptFontName = ps_name(inst.styleName)
        inst.styleMapFamilyName = None
    for src in ds.sources:
        src.familyName = P.FAMILY
