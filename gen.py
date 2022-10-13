#!/usr/bin/env python3

"""
You could die
"""

# import fontTools.ttLib.woff2
# from fontTools.ttLib.woff2 import (WOFF2Reader)

import argparse
import os
import random
import tempfile

import fontTools.subset as ftsubset
import fontTools.merge as ftmerge

from fontTools.misc.transform import Transform
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen


def get_unicode_chars(font):
    """Return a set of tuples representing a unicode character."""
    return {
        (a, b)
        for table in font.get("cmap").tables
        for a, b in table.cmap.items()
    }


def strip(font, unicodes, options):
    """..."""

    gids = []
    glyphs = []
    text = ""
    unicodes = ftsubset.parse_unicodes(",".join(unicodes))

    subsetter = ftsubset.Subsetter(options=options)

    subsetter.populate(
        glyphs=glyphs,
        gids=gids,
        unicodes=unicodes,
        text=text,
    )

    subsetter.subset(font)

    return font


def scale(font, size=2048):
    """
    ...
    """
    final = size
    head_table = font.get("head")

    scale_val = final/head_table.unitsPerEm

    glyph_pen = TTGlyphPen(font.getGlyphSet())

    transform_pen = TransformPen(
        glyph_pen,
        Transform().scale(scale_val, scale_val),
    )

    head_table.unitsPerEm = final

    for glyph_name in font.getGlyphOrder():
        glyph = font['glyf'][glyph_name]

        # Avoid double-transforming composite glyphs
        if glyph.isComposite():
            continue

        glyph.draw(transform_pen, font['glyf'])

        now = glyph_pen.glyph()
        now.recalcBounds(font['glyf'])

        hmtx = font['hmtx'][glyph_name]
        hmtx_new = (int(hmtx[0]*scale_val), int(hmtx[1]*scale_val))
        font['glyf'][glyph_name] = now
        font['hmtx'][glyph_name] = hmtx_new

    for glyph_name in font.getGlyphOrder():
        glyph = font['glyf'][glyph_name]
        glyph.trim()
        glyph.removeHinting()
        # glyph.recalcBounds(font['glyf'])


if __name__ == "__main__":

    parser = argparse.ArgumentParser("Cease and Desist Sans.woff2 generator")

    parser.add_argument(
        "fnames",
        nargs="+",
        help="list of file names to merge",
    )

    parser.add_argument(
        "--out-file",
        default="CeaseAndDesistSans-Regular.woff2",
        help="path to file name",
    )

    args = parser.parse_args()

    fnames = args.fnames
    out_file = args.out_file

    options = ftsubset.Options()
    options.recalc_bounds = True
    options.recalc_average_width = True
    options.recalc_max_content = True
    options.legacy_kern = True

    fonts = [
        ftsubset.load_font(name, options, dontLoadGlyphNames=False, lazy=False)
        for name in fnames
    ]

    all_unicodes = [
        get_unicode_chars(font)
        for font in fonts
    ]

    int_unicodes = all_unicodes[0]

    for unis in all_unicodes:
        int_unicodes.intersection_update(unis)

    shared_unicodes = []

    for code, _ in sorted(int_unicodes):
        val = hex(code)[2:].upper()
        val = "U+" + "0"*(4-len(val)) + val
        shared_unicodes.append(val)

    unicode_lists = [[] for _ in fnames]

    for uni in shared_unicodes:
        k = random.randint(0, len(unicode_lists)-1)
        unicode_lists[k].append(uni)

    fonts = [
        strip(font, unicode_lists[i], options)
        for i, font in enumerate(fonts)
    ]

    temp_font_files = []

    for ttfont in fonts:
        with tempfile.NamedTemporaryFile(prefix="", suffix=".woff2") as fi:
            fname = fi.name
        scale(ttfont)
        ftsubset.save_font(ttfont, fname, options)
        temp_font_files.append(fname)
        ttfont.close()

    # MERGE

    merger = ftmerge.Merger(options)
    font = merger.merge(temp_font_files)
    font.flavor = "woff2"
    font.save(out_file)
    font.close()

    # CLEAN

    for fname in temp_font_files:
        os.remove(fname)
