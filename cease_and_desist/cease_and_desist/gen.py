#!/usr/bin/env python3

"""
You could die
"""


import argparse
import os
import tempfile


from queue import LifoQueue
from random import Random
from threading import Thread


import fontTools.subset as ftsubset
import fontTools.merge as ftmerge

from fontTools.misc.transform import Transform
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen


OPTIONS = ftsubset.Options()
OPTIONS.recalc_bounds = True
OPTIONS.recalc_average_width = True
OPTIONS.recalc_max_content = True
OPTIONS.legacy_kern = True


def load_font(fname):
    """Return a TTFont from a filename."""
    return ftsubset.load_font(
        fname,
        OPTIONS,
        dontLoadGlyphNames=False,
        lazy=False,
    )


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


class CeaseAndDesistSansGenerator(object):
    """
    CeaseAndDesistSansGenerator
    """

    def __init__(self, fonts, seed=0, options=OPTIONS):
        """Construct a CeaseAndDesistSansGenerator"""

        self.fonts = fonts
        self.seed = seed
        self.options = options

        self.unicodes = intersection_unicodes(self.fonts)

        self.unicode_lists = [[] for _ in self.fonts]

        self.refresh_font(self.seed)

        self.fonts = [
            strip(font, unicode_list, options)
            for font, unicode_list in zip(self.fonts, self.unicode_lists)
        ]

        self.font = self.merge()
    
    def refresh_font(self, seed):

        self.seed = seed

        rng = Random(self.seed)

        self.unicode_lists = [[] for _ in self.fonts]

        for uni in self.unicodes:
            i = rng.randint(0, len(self.unicode_lists)-1)
            self.unicode_lists[i].append(uni)

        pass


    def __del__(self):
        for fname in self.temp_font_files:
            os.remove(fname)

    def merge(self):
        """Merge all fonts"""

        temp_font_files = []

        for ttfont in self.fonts:
            with tempfile.NamedTemporaryFile(prefix="", suffix=".woff2") as fi:
                fname = fi.name
            scale(ttfont)
            ftsubset.save_font(ttfont, fname, self.options)
            temp_font_files.append(fname)
            ttfont.close()

        merger = ftmerge.Merger(self.options)
        font = merger.merge(temp_font_files)
        font.flavor = "woff2"
        font.close()

        self.temp_font_files = temp_font_files

        return font
    
    def save(self, out_file):
        self.font.save(out_file)

    @staticmethod
    def _get_unicode_chars(font):
        """Return a set of tuples representing a unicode character."""
        return {
            (a, b)
            for table in font.get("cmap").tables
            for a, b in table.cmap.items()
        }

    def font():
        """Return a TTFont """
        return None


def intersection_unicodes(fonts):
    """..."""

    # Get a set of universal unicode characters for a font

    all_unicodes = [
        get_unicode_chars(font)
        for font in fonts
    ]

    int_unicodes = all_unicodes[0]

    for unis in all_unicodes:
        int_unicodes.intersection_update(unis)

    # Convert to U+???? strings

    shared_unicodes = []

    for code, _ in sorted(int_unicodes):
        val = hex(code)[2:].upper()
        val = "U+" + "0"*(4-len(val)) + val
        shared_unicodes.append(val)

    return shared_unicodes


class CachedValue(object):
    """
    CachedValue

    Restock value and serve old value until subthread finished.
    """

    def __init__(self, fn, args, hits=1, ttl=-1):

        self.value = fn(*args)

        self.queue = LifoQueue()

        def putter():
            while True:
                v = fn(*args)
                self.queue.put(v)

        def getter():
            while True:
                v = self.queue.get(block=True)
                self.value = v

        self.putter_thread = Thread(target=putter)
        self.putter_thread.start()

        self.getter_thread = Thread(target=getter)
        self.getter_thread.start()


    def get(self):
        return self.value
