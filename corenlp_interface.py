
""" Module deals with the recognition of named entities in text, in particular with the recognition of locations. """

# TODO tidy and make robust
# TODO start server from method here?
# TODO make standalone script version?

import requests

from config import CORENLP_SERVER_URL
from utilities import read_from_file, write_to_file


# TODO error handling?
def corenlp_tag_file(file, results_dir):
    """ Read the given file, mark it up by making a request to the CoreNLP server, and write response to a file in
        the given results dir and return this filepath. """

    text = read_from_file(file)
    payload = {'text' : text}
    response = requests.get(CORENLP_SERVER_URL, params=payload)
    corenlp_tagged_file = results_dir + '02_ne_tagged.xml'
    write_to_file(corenlp_tagged_file, response.text)
    return corenlp_tagged_file

def corenlp_to_spatialml(corenlp_file, results_dir):
    pass

# testing
def main():
    print(corenlp_tag_file("I am from Oxford and my name is Bob."))

if __name__ == '__main__':
    main()

