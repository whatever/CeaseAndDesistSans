#!/usr/bin/env python3

import argparse

from .gen import (
    CeaseAndDesistSansGenerator,
    load_font,
)

def main():
    # Parse arguments

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

    generator = CeaseAndDesistSansGenerator([
        load_font(name)
        for name in fnames
    ], 0)

    generator.save(out_file)
