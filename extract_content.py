#!/usr/bin/env python3

from argparse import ArgumentParser
import requests
from bs4 import BeautifulSoup

# TODO more documentation
# TODO make robust
# TODO read token from file

READABILITY_PARSER_URL = 'https://www.readability.com/api/content/v1/parser'
PARSER_API_TOKEN = 'f3eceed717ac392a24961b43bb4a39bc6d2b83da'

def create_arg_parser():

    parser = ArgumentParser(description='Extract main content from given url.')
    parser.add_argument('url')

    return parser

def extract_content(url):

    # obtain main html content from url using Readability Parser API
    parameters = {'token' : PARSER_API_TOKEN, 'url' : url}
    json_response = requests.get(READABILITY_PARSER_URL, params=parameters).json()
    html_content = json_response['content'] # TODO consider doing something with other parts of response eg title, author - make object returned?

    # parse out text only and return
    text_content = BeautifulSoup(html_content).get_text()
    return text_content

def main():

    # parse url from command line
    parser = create_arg_parser()
    args = parser.parse_args()
    url = args.url

    # extract main text content from url
    text_content = extract_content(url)

    # print text to standard output
    print(text_content)

if __name__ == '__main__':
    main()