
""" Module deals with the recognition of named entities in text, in particular with the recognition of locations. """

# TODO tidy and make robust
# TODO start server from method here?
# TODO make standalone script version?

import requests

from config import CORENLP_SERVER_URL


# TODO error handling?
def corenlp_tag_text(text):
    payload = {'text' : text}
    response = requests.get(CORENLP_SERVER_URL, params=payload)
    print('\n', response.text, '\n')
    return response.text

# testing
def main():
    print(corenlp_tag_text("I am from Oxford City and my name is Bob."))

if __name__ == '__main__':
    main()

