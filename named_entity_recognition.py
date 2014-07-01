
""" Module deals with the recognition of named entities in text, in particular with the recognition of locations. """

# TODO tidy and make robust
# TODO start server from method here?
# TODO make standalone script version?

from ner import SocketNER

from config import NER_SERVER_HOST, NER_SERVER_PORT, NER_DEPLOY_SCRIPT


# def _start_server():
#     call(DEPLOY_SCRIPT)
#
# _start_server()

def tag_named_entities(text):
    """ Get the input text with locations, organizations, and people marked up using the Stanford Named Entity
    Recognizer.
    """

    tagger = SocketNER(host=NER_SERVER_HOST, port=NER_SERVER_PORT, output_format='inlineXML')
    tagged_text = tagger.tag_text(text)
    tagged_text = '<NER_TAGGED_TEXT>' + tagged_text + '</NER_TAGGED_TEXT>' # wrap whole doc in this xml tag
    return tagged_text
