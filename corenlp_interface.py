
""" Module deals with the recognition of named entities in text, in particular with the recognition of locations. """

import requests

import config

# TODO seems to be issue with too long text, not working look into

# TODO error handling?
def corenlp_tag_text(text):
    """ Mark up text by making a request to the CoreNLP server, and return XML received as a string. """

    payload = {'text': text, 'pipeline': 'ner'}
    response = requests.get(config.CORENLP_SERVER_URL, params=payload)

    return response.text

def corenlp_to_spatialml(corenlp_file, results_dir):
    pass

# testing
def main():
    # print(corenlp_tag_text(""""""))
    pass

if __name__ == '__main__':
    main()

