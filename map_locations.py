#!/usr/bin/env python3

""" Main logic of program. """

from argparse import ArgumentParser
from string import Template
from datetime import datetime
import os
import webbrowser

from content_extraction import extract_content
from corenlp_interface import corenlp_tag_text
from disambiguation import disambiguate
from kml_generation import create_kml
from config import CONTEXT_DIR, RESULTS_DIR, MAP_VIEW_TEMPLATE
from utilities import form_filename, write_to_file


def _create_arg_parser():
    parser = ArgumentParser(description='Extract main content from the given url, identify and disambiguate locations in'
                                        ' the text, and plot these on Google maps.')

    # positional args
    parser.add_argument('url')

    # optional args
    parser.add_argument('--nomap', '-n', action='store_true', default=False,
                        help='If present the map for the given url will not be displayed after processing.')

    return parser

def map_locations(url, display_map=False):
    """ Main logic of program, perform entire pipeline on the text indicated by the command line arguments given,
        writing each stage of the pipeline to files in the results directory. """

    print("Starting map_locations for url {}...".format(url))

    # obtain article from given url
    print("Obtaining article from url...")
    article = extract_content(url)

    # form results directory structure for this article
    print("Forming results directory structure...")
    results_dir = CONTEXT_DIR + RESULTS_DIR + form_filename(article.title) + '/' + form_filename(datetime.now()) + '/'
    os.makedirs(results_dir, exist_ok=True)
    content_file = results_dir + '01_content.txt'
    ne_tagged_file = results_dir + '02_ne_tagged.xml'
    candidates_dir = results_dir + '03_candidates/'
    os.makedirs(candidates_dir, exist_ok=True)
    relative_kml_file = '04_kml.kml'
    kml_file = results_dir + relative_kml_file
    html_file = results_dir + '05_map_view.html'

    # get article text
    print("Writing article content to file {}...".format(content_file))
    text = article.content
    write_to_file(content_file, text)

    # tag named entities
    print("Tagging named entities in article...")
    try:
        ne_tagged_text = corenlp_tag_text(text)
    except ConnectionRefusedError as ex:
        # print (most likely) reason for error, trace, and quit
        print("Stanford CoreNLP server must be run to tag named entities! (settings in config.py)")
        ex.with_traceback()

    print("Writing tagged article to file {}...".format(ne_tagged_file))
    write_to_file(ne_tagged_file, ne_tagged_text)

    # disambiguate identified locations to find most likely candidate (candidates written to files in disambiguate())
    print("Disamiguating identified locations...")
    identified_locations = disambiguate(ne_tagged_text, candidates_dir)

    # form kml for identified locations
    print("Creating kml for article locations...")
    kml = create_kml(identified_locations)

    print("Writing kml to file {}...".format(kml_file))
    write_to_file(kml_file, kml)

    print("Creating html file for map...")
    with open(CONTEXT_DIR + MAP_VIEW_TEMPLATE) as template_file:
        template = Template(template_file.read())
        html = template.substitute(kml_file=relative_kml_file, title=article.title)
        write_to_file(html_file, html)

    if display_map:
        print("Opening map...")
        webbrowser.open_new_tab(html_file)

    print("Map: file://" + html_file)

    print("map_locations successfully completed for {}.\n".format(url))


if __name__ == "__main__":
    parser = _create_arg_parser()
    args = parser.parse_args()
    url = args.url
    display_map = not args.nomap
    map_locations(url, display_map)
