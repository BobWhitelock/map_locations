#!/bin/bash

CORENLP_SCRIPT=/media/Storage/corenlp-python/corenlp/corenlp.py

"$CORENLP_SCRIPT" --port 1234 \
    --corenlp /media/Storage/stanford-corenlp-full-2014-06-16 \
    --properties /media/Storage/Python_programs/Dissertation_python3/corenlp.properties

# TODO add rest of props