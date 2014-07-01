#!/usr/bin/env python3

# TODO: if get 'ConnectionRefusedError: [Errno 111] Connection refused' when running map_locations need to remind to
# start server - possibly automatically start server?

from argparse import ArgumentParser

from lxml import etree

from extract_content import extract_content
from tag_named_entities import tag_named_entities
from access_geonames import *
from generate_kml import create_kml


def create_arg_parser():
    parser = ArgumentParser(description='Extract main content from the given url, identify and disambiguate locations in'
                                        ' the text, and plot these on Google maps. (currently stages 1, 2, 3 done roughly).')
    parser.add_argument('url')

    return parser



def main():
    # parse command line args
    parser = create_arg_parser()
    args = parser.parse_args()
    url = args.url

    # extract content from given url
    text = extract_content(url)

    # tag named entities in text
    tagged_text = tag_named_entities(text)

    # write tagged text to result.xml
    results_file = open('result.xml', 'w')
    results_file.write(tagged_text)
    results_file.close()

    # for each tagged location identify candidates and print one with highest population
    tagged_locations = extract_locations(tagged_text)
    identified_locations = []
    for location in tagged_locations:
        candidates = find_candidates(location)
        if len(candidates) > 0:
            top_candidate = geoname_with_highest_population(candidates)
            identified_locations.append(top_candidate)

    # print kml of identified locations
    kml = create_kml(identified_locations)
    print(kml)

if __name__ == "__main__":
    main()