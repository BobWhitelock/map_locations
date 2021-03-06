#!/usr/bin/env python3

""" Main logic of program. """

import argparse
import string
import datetime
import os
import webbrowser

from bs4 import BeautifulSoup

import readability_interface
import corenlp_interface
import identification
import kml_generation
import config
import utilities


def make_results_dir(name):
    """ Form results dir structure to store results of an execution of map_locations, consisting of a dir with the
        given name inside RESULTS_DIR, and a dir with the current datetime inside this, and return formed dir path. """

    results_dir = config.RESULTS_DIR + utilities.form_filename(name) + '/' + utilities.form_filename(datetime.datetime.now()) + '/'
    os.makedirs(results_dir, exist_ok=True)
    return results_dir

# def store_content(readability_response, results_dir):
#     """ Store the text content from a request to the Readability parser API in a file in the given results dir and
#         return this filepath. """
#
#     html_content = readability_response['content']
#     text_content = BeautifulSoup(html_content).get_text()
#     content_file = results_dir + '01_content.txt'
#     utilities.write_to_file(content_file, text_content)
#     return content_file

def _create_arg_parser():
    parser = argparse.ArgumentParser(description='Extract main content from the given url, identify and disambiguate locations in'
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
        print("A url or file must be given to read content to process from, see help (-h or --help option) for more "
              "information.")
        exit(1)

    # starting message
    loc = url if file is None else file
    print("Starting map_locations for {}...".format(loc))

    # obtain the content to process
    if file is not None:
        # read content from file
        print("Reading article from file...")
        title = file
        content = utilities.read_from_file(file)

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
    utilities.write_to_file(content_file, content)

    # tag file using Stanford CoreNLP server
    print("Tagging named entities in article...")
    try:
        corenlp_tagged_text = corenlp_interface.corenlp_tag_text(content)
    except ConnectionRefusedError as ex:
        # print (most likely) reason for error, trace, and quit
        print("Stanford CoreNLP server must be run to tag named entities! (settings in config.py)")
        ex.with_traceback()

    # store tagged article
    print("Writing tagged article to file...")
    corenlp_tagged_file = results_dir + '02_corenlp_tagged.xml'
    utilities.write_to_file(corenlp_tagged_file, corenlp_tagged_text)

    # disambiguate identified locations to find most likely candidate (candidates written to files in disambiguate())
    print("Disambiguating identified locations...")
    identified_locations = identification.identify(corenlp_tagged_text, results_dir)


    # print("\n********************", identified_locs_to_xml(identified_locations, corenlp_tagged_text), "*******************\n")


    # form kml for identified locations
    print("Creating kml for article locations...")
    kml = kml_generation.create_kml(identified_locations)

    print("Writing kml to file...")
    relative_kml_file = '04_kml.kml'
    kml_file = results_dir + relative_kml_file
    utilities.write_to_file(kml_file, kml)

    print("Creating html files for map...")

    # map html file
    with open(config.CONTEXT_DIR + config.MAP_VIEW_TEMPLATE) as template_file:
        template = string.Template(template_file.read())
        html = template.substitute(kml_file=relative_kml_file, title=title)
        map_html_file = results_dir + '05_map_view.html'
        utilities.write_to_file(map_html_file, html)

    # article html file
    with open(config.CONTEXT_DIR + config.ARTICLE_TEMPLATE) as template_file:
        template = string.Template(template_file.read())

        # Form article content html, adding bold tags around identified locations.
        # find positions of all ided locs and add bold tags in reverse order so positions don't shift
        content_html_list = list(content)
        positions = {}
        for ided_loc in identified_locations:
            positions[ided_loc.start] = ided_loc.stop

        start_positions = reversed(sorted(positions.keys()))
        for start_pos in start_positions:
            stop_pos = positions[start_pos]
            content_html_list.insert(stop_pos-1, '</b>')
            content_html_list.insert(start_pos-1, '<b>')

        # replace newlines with paragraphs
        for index, el in enumerate(content_html_list):
            if el == '\n':
                content_html_list[index] = '<p>'

        content_html = ''.join(content_html_list)

        # create and save the html
        html = template.substitute(article_title=title, article_content=content_html)
        article_html_file = results_dir + '06_identified_locs.html'
        utilities.write_to_file(article_html_file, html)

    if display_map:
        print("Opening map...")
        # webbrowser.open_new_tab(article_html_file)
        webbrowser.open_new_tab(map_html_file)

    print("Map: file://" + map_html_file)

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
