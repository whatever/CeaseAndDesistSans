"""
ill
"""


import argparse
import io
import os.path

from .gen import (
    CeaseAndDesistSansGenerator,
    load_font,
)

from flask import Flask
from flask import send_from_directory


APP = Flask(__name__)


GENERATOR = None


DIR = os.path.dirname(__file__)


@APP.route("/")
def index():
    return send_from_directory(DIR, "index.html")


@APP.route("/favicon.ico")
def favicon():
    return send_from_directory(DIR, "favicon.ico")


@APP.route("/CeaseAndDesistSans-Regular.woff2")
def font():
    buff = io.BytesIO()
    GENERATOR.save(buff)
    return (buff.getvalue(), 200, [])


def main():
    parser = argparse.ArgumentParser("Serve CeaseAndDesistSans-Regular.woff2")
    parser.add_argument(
            "fnames",
            nargs="+",
            help="list of file names to merge",
            )
    args = parser.parse_args()

    global GENERATOR
    GENERATOR = CeaseAndDesistSansGenerator([
        load_font(name)
        for name in args.fnames
        ], 0)

    APP.run(host="0.0.0.0", port=8080)

