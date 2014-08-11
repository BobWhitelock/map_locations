#!/usr/bin/env python3

""" Module deals with obtaining the text content to be processed through the rest of the system. """

# TODO make robust - deal with http status codes
# TODO add functions to obtain text from other places? + obtain text in bulk from urls?

import requests

from config import READABILITY_API_TOKEN, READABILITY_PARSER_URL


def readability_request(url):
    """ Make request to Readability Parser API for a particular URL and return Json response. """

    # if url doesn't start with a protocol attempt to use http
    try:
        url.index(':')
    except ValueError:
        url = 'http://' + url

    # query Readability Parser API to try and parse text from given url
    parameters = {'token' : READABILITY_API_TOKEN, 'url' : url}
    json_response = requests.get(READABILITY_PARSER_URL, params=parameters).json()

    # if error returned print this
    # TODO throw exception with error message?
    if 'error' in json_response:
        error_message = json_response['messages']
        print(error_message)

    return json_response

# Below only used when running module as stand-alone program - needed?

# def create_arg_parser():
#     parser = ArgumentParser(description='Extract main content from given url.')
#     parser.add_argument('url')
#     return parser

# def main():
#
#     # parse url from command line
#     parser = create_arg_parser()
#     args = parser.parse_args()
#     url = args.url
#
#     # extract main text content from url
#     text_content = extract_content(url)
#
#     # print text to standard output
#     print(text_content)
#
# if __name__ == '__main__':
#     main()