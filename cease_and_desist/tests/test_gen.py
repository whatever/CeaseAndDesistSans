#!/usr/bin/env python3


import os
import unittest
import cease_and_desist as cd


class TestGen(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        here = os.path.dirname(__file__)

        fontfiles = [
            os.path.join(here, "..", "fonts", fname)
            for fname in os.listdir(os.path.join(here, "..", "fonts"))
        ]

        cls.fonts = [
            cd.load_font(fname)
            for fname in fontfiles
        ]

        cls.generator = cd.CeaseAndDesistSansGenerator(cls.fonts)

    def test_basic(self):

        gen = self.generator

        self.assertEqual(gen.seed, 0)

        """
        self.assertEqual(
            len(gen._get_unicode_chars(gen.fonts[0])),
            502,
        )
        """
        self.assertEqual(len(gen.unicode_lists), len(gen.fonts))
        self.assertEqual(len(gen.unicodes), 196)
        self.assertEqual(sum([len(lis) for lis in gen.unicode_lists]), 196)

        print(gen.font)


if __name__ == "__main__":
    unittest.main()
