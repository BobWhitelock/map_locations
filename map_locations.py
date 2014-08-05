#!/usr/bin/env python3

""" Main logic of program. """

from argparse import ArgumentParser
from string import Template
from datetime import datetime
import os
import webbrowser
from bs4 import BeautifulSoup

import readability_interface
from corenlp_interface import corenlp_tag_file
from disambiguation import disambiguate
from kml_generation import create_kml
from config import CONTEXT_DIR, RESULTS_DIR, MAP_VIEW_TEMPLATE
from utilities import form_filename, write_to_file, read_from_file


def make_results_dir(name):
    """ Form results dir structure to store results of an execution of map_locations, consisting of a dir with the
        given name inside RESULTS_DIR, and a dir with the current datetime inside this, and return formed dir path. """

    results_dir = RESULTS_DIR + form_filename(name) + '/' + form_filename(datetime.now()) + '/'
    os.makedirs(results_dir, exist_ok=True)
    return results_dir

def store_content(readability_response, results_dir):
    """ Store the text content from a request to the Readability parser API in a file in the given results dir and
        return this filepath. """

    html_content = readability_response['content']
    text_content = BeautifulSoup(html_content).get_text()
    content_file = results_dir + '01_content.txt'
    write_to_file(content_file, text_content)
    return content_file

def _create_arg_parser():
    parser = ArgumentParser(description='Extract main content from the given url, identify and disambiguate locations in'
                                        ' the text, and plot these on Google maps.')

    parser.add_argument('--url', '-u', help='Read main content from given url and process it.')
    parser.add_argument('--file', '-f', help='Read content to process from a file rather than a url; if a url is '
                                             'given as well it will be ignored.')
    parser.add_argument('--nomap', '-n', action='store_true', default=False,
                        help='If present the map for the given url will not be displayed after processing.')

    return parser

def map_locations(url=None, file=None, display_map=False):
    """ Main logic of program, perform entire pipeline on the text indicated by the command line arguments given,
        writing each stage of the pipeline to files in the results directory. """

    # exit if neither url nor file given
    if url is None and file is None:
        print("A url or file must be given to read content to process from, see help for more information.")
        exit(1)

    # starting message
    loc = url if file is None else file
    print("Starting map_locations for {}...".format(loc))

    # obtain the content to process
    if file is not None:
        # read content from file
        print("Reading content from file...")
        title = file
        content = read_from_file(file)

    elif url is not None:
        # make request to Readability API for url
        print("Obtaining article from url...")
        readability_response = readability_interface.readability_request(url)
        title = readability_response['title']
        html_content = readability_response['content']
        content = BeautifulSoup(html_content).get_text()

    # form results directory for article
    print("Forming results directory for article...")
    results_dir = make_results_dir(title)

    # store content of article
    print("Writing article content to file...")
    content_file = results_dir + '01_content.txt'
    write_to_file(content_file, content)

    ####
    relative_kml_file = '04_kml.kml'
    kml_file = results_dir + relative_kml_file
    html_file = results_dir + '05_map_view.html'
    ####

    # tag file using Stanford CoreNLP server
    print("Tagging named entities in article...")
    try:
        corenlp_tagged_file = corenlp_tag_file(content_file, results_dir)
    except ConnectionRefusedError as ex:
        # print (most likely) reason for error, trace, and quit
        print("Stanford CoreNLP server must be run to tag named entities! (settings in config.py)")
        ex.with_traceback()

    # print("Writing tagged article to file {}...".format(ne_tagged_file))
    # write_to_file(ne_tagged_file, ne_tagged_text)

    ne_tagged_text = read_from_file(corenlp_tagged_file)

    # disambiguate identified locations to find most likely candidate (candidates written to files in disambiguate())
    print("Disamiguating identified locations...")
    identified_locations = disambiguate(ne_tagged_text, results_dir)

    # form kml for identified locations
    print("Creating kml for article locations...")
    kml = create_kml(identified_locations)

    print("Writing kml to file {}...".format(kml_file))
    write_to_file(kml_file, kml)

    print("Creating html file for map...")
    with open(CONTEXT_DIR + MAP_VIEW_TEMPLATE) as template_file:
        template = Template(template_file.read())
        html = template.substitute(kml_file=relative_kml_file, title=title)
        write_to_file(html_file, html)

    if display_map:
        print("Opening map...")
        webbrowser.open_new_tab(html_file)

    print("Map: file://" + html_file)

    print("map_locations successfully completed for {}.\n".format(loc))


if __name__ == "__main__":
    # TODO redo so url positional and file optional override

    parser = _create_arg_parser()
    args = parser.parse_args()
    url = args.url
    display_map = not args.nomap

    if args.file is not None:
        map_locations(file=args.file, display_map=display_map)
    else:
        map_locations(url=url, display_map=display_map)
