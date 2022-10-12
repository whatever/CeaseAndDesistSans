#!/usr/bin/env python3

# import fontTools.ttLib.woff2
# from fontTools.ttLib.woff2 import (WOFF2Reader)

import os
import random

import fontTools.subset as ftsubset
import fontTools.merge as ftmerge

from fontTools.misc.transform import Transform
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

def get_unicode_chars(font):
    print([
        (a, b)
        for table in font.get("cmap").tables
        for a, b in table.cmap.items()
    ])

def strip(fontfile, unicodes, options):


    font = ftsubset.load_font(
        fontfile,
        options,
        dontLoadGlyphNames=False,
        lazy=False,
    )

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
    final = size
    head_table = font.get("head")

    s = final/head_table.unitsPerEm

    glyphPen = TTGlyphPen(font.getGlyphSet())
    transformPen = TransformPen(glyphPen, Transform().scale(s, s))
    head_table.unitsPerEm = final

    for glyphName in font.getGlyphOrder():
        glyph = font['glyf'][glyphName]

        # Avoid double-transforming composite glyphs
        if glyph.isComposite():
            continue

        glyph.draw(transformPen, font['glyf'])

        old = font['glyf'][glyphName]
        now = glyphPen.glyph()
        now.recalcBounds(font['glyf'])

        # print(getattr(old, "xMax", None))
        # print(getattr(now, "xMax", None))
        hmtx = font['hmtx'][glyphName]
        hmtx_new = (int(hmtx[0]*s), int(hmtx[1]*s))
        font['glyf'][glyphName] = now
        font['hmtx'][glyphName] = hmtx_new

    for glyphName in font.getGlyphOrder():
        glyph = font['glyf'][glyphName]
        glyph.trim()
        glyph.removeHinting()
        # glyph.recalcBounds(font['glyf'])

if __name__ == "__main__":
    fname = "SquareSansText-Regular.woff2"

    """
    with open(fname, "rb") as fi:
        reader = WOFF2Reader(fi)
        print(dir(reader.ttFont))
    """

    # pyftsubset OracleSansVF.woff2 --unicodes=U+004D --output-file=CeaseAndDesistSans.woff2   


    
    unicode_lists = [[], []]

    for i in range(0x7F+1):
        k = random.randint(0, 1)
        if k == 2: continue
        unicode_lists[k].append("U+00" + hex(i)[2:].upper())

    options = ftsubset.Options()
    options.recalc_bounds = True
    options.recalc_average_width = True
    options.recalc_max_content = True
    options.legacy_kern = True

    fnames = [
        f"fonts/{fname}"
        for fname in os.listdir("./fonts/")
    ]

    unicode_lists = [list() for _ in fnames]

    for i in range(0x7F+1):
        k = random.randint(0, len(unicode_lists)-1)
        unicode_lists[k].append("U+00" + hex(i)[2:].upper())
    
    fonts = [
        strip(fnames[i], unicode_lists[i], options)
        for i in range(len(fnames))
    ]
    
    for i in range(len(fonts)):
        font = fonts[i]
        scale(font)
        ftsubset.save_font(font, f"font{i}.woff2", options)
        font.close()

    # Bugs
    # 1. 9 drops too much when it is "UberMove"
