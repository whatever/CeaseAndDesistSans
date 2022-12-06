"""
Serve CeaseAndDesistSans-Reulgar.woff2
"""


import argparse
import io
import logging
import os.path
import random
import signal
import sys
import time


from flask import Flask, request
from flask import send_from_directory


import gevent
import gevent.signal
from gevent.pywsgi import WSGIServer


from .gen import (
    CachedValue,
    CeaseAndDesistSansGenerator,
    load_font,
)


APP = Flask(__name__)
"""..."""


DIR = os.path.dirname(__file__)
"""..."""


def generate_font(fnames):

    # Fetch and generate unstripped fonts
    fonts = [load_font(name) for name in fnames]

    # XXX: Constructor mutates loaded fonts, so we need to complete reload
    generator = CeaseAndDesistSansGenerator(fonts, time.time())

    buff = io.BytesIO()
    generator.save(buff)

    return buff


VAL = None
"""Later set as CachedValue after app is used"""


@APP.route("/")
def index():
    return send_from_directory(DIR, "index.html")


@APP.route("/favicon.ico")
def favicon():
    return send_from_directory(DIR, "favicon.ico")


@APP.route("/CeaseAndDesistSans-Regular.woff2")
def font():

    val = VAL.get().getvalue()

    headers = [
        ("Cache-Control", "no-cache, no-store, must-revalidate"),
        ("Pragma", "no-cache"),
        ("Expires", "0"),
        ("Content-Type", "font/woff2"),
        ("ETag", str(hash(val))),
    ]

    return (val, 200, headers)


def main():

    parser = argparse.ArgumentParser("Serve CeaseAndDesistSans-Regular.woff2")

    parser.add_argument(
        "fnames",
        nargs="+",
        help="list of file names to merge",
    )

    parser.add_argument(
        "-p",
        "--port",
        default=8080,
        type=int,
        help="listen on port number",
    )

    parser.add_argument(
        "--cache-size",
        default=1,
        type=int,
        help="number of hits before font is refreshed in cache",
    )

    parser.add_argument(
        "--cache-ttl",
        default=69,
        type=int,
        help="maximum time before font is refreshed in cache",
    )

    args = parser.parse_args()

    print(f"""
    font names ...... {", ".join(args.fnames)}
    port ............ {args.port}
    cache-size ...... {args.cache_size}
    cache-ttl ....... {args.cache_ttl}
    """.strip())

    ftlog = logging.getLogger("fontTools.subset")
    ftlog.setLevel(logging.ERROR)

    global VAL
    VAL = CachedValue(generate_font, (args.fnames, ))

    def _keyboard_interrupt_handler(signum, frame):
        raise SystemExit

    signal.signal(signal.SIGINT, _keyboard_interrupt_handler)

    server = WSGIServer(('0.0.0.0', 8080), APP)
    server.serve_forever()
