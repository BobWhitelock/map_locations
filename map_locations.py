#!/usr/bin/env python3

""" Main logic of program. """

# TODO: if get 'ConnectionRefusedError: [Errno 111] Connection refused' when running map_locations need to remind to
# start server - possibly automatically start server?

from argparse import ArgumentParser
import os

from content_extraction import extract_content
from named_entity_recognition import tag_named_entities
from disambiguation import disambiguate
from kml_generation import create_kml
from config import RESULTS_DIRECTORY
from utilities import form_filename


def _create_arg_parser():
    parser = ArgumentParser(description='Extract main content from the given url, identify and disambiguate locations in'
                                        ' the text, and plot these on Google maps. (currently stages 1, 2, 3 done roughly).')
    parser.add_argument('url')

    return parser

# TODO move to utilities? + below?
def _write(filepath, text):
    """ Write the given text to a file with the given filepath (overwriting any previous content). """

    file = open(filepath, 'w')
    file.write(text)
    file.close()

def _make_if_not_already(directory):
    """ Make a directory with the given name, if it does not exist already. """

    try:
        os.mkdir(directory)
    except FileExistsError:
        pass

def map_locations(url=None):
    """ Main logic of program, perform entire pipeline on the text indicated by the command line arguments given,
        writing each stage of the pipeline to files in the results directory. """

    # if url given use that, otherwise try to parse from command line
    if url is None:
        parser = _create_arg_parser()
        args = parser.parse_args()
        url = args.url

    print("Starting map_locations for url {}\n".format(url))

    # obtain article from given url
    print("Obtaining article from url...")
    article = extract_content(url)
    print("Article successfully obtained.\n")

    # form results directory structure for this article
    print("Forming results directory structure...")
    article_filename = form_filename(article.title)
    results_dir = RESULTS_DIRECTORY + article_filename
    _make_if_not_already(results_dir)
    article_content_file = results_dir + '/01_content.txt'
    ne_tagged_file = results_dir + '/02_ne_tagged.xml'
    candidates_dir = results_dir + '/03_candidates/'
    _make_if_not_already(candidates_dir)
    kml_file = results_dir + '/04_{}.kml'.format(article_filename)
    print("Results directory structure created.\n")

    # get article text and tag named entities
    print("Writing article content to file {}...".format(article_content_file))
    text = article.content
    _write(article_content_file, text)
    print("Article content written.\n")

    print("Tagging named entities in article...")
    ne_tagged_text = tag_named_entities(text)
    print("Named entities tagged.\n")

    print("Writing tagged article to file {}...".format(ne_tagged_file))
    _write(ne_tagged_file, ne_tagged_text)
    print("Tagged article written.\n")

    # disambiguate identified locations to find most likely candidate (candidates written to files in disambiguate())
    print("Disamiguating all identified loctions...\n")
    identified_locations = disambiguate(ne_tagged_text, candidates_dir)
    print("All identified locations disambiguated.\n")

    # form kml for identified locations
    print("Creating kml for article locations...")
    kml = create_kml(identified_locations)
    print("Kml created.\n")

    print("Writing kml to file {}...".format(kml_file))
    _write(kml_file, kml)
    print("Kml file written\n")

    print("map_locations successfully completed for {}.\n\n".format(url))

if __name__ == "__main__":
    map_locations()
