#!/usr/bin/env python3

from argparse import ArgumentParser

from extract_content import extract_content
from tag_named_entities import tag_named_entities
import sys

def create_arg_parser():
    parser = ArgumentParser(description='Extract main content from the given url, identify and disambiguate locations in'
                                        ' the text, and plot these on Google maps. (currently stages 1 and 2 done roughly).')
    parser.add_argument('url')

    return parser

def main():
    parser = create_arg_parser()
    args = parser.parse_args()
    url = args.url
    text = extract_content(url)
    tagged_text = tag_named_entities(text)
    print(tagged_text)

if __name__ == "__main__":
    main()