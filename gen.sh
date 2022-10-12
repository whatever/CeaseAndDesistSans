#!/bin/sh
./gen.py && pyftmerge *.woff2 && mv merged.ttf ok.ttf
