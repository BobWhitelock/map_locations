# TODO tidy and make robust
# TODO start server from method here?
# TODO make standalone script version?

from ner import SocketNER
from subprocess import call

from config import NER_SERVER_HOST, NER_SERVER_PORT, NER_DEPLOY_SCRIPT

# tagger = SocketNER(host='localhost', port=1234, output_format='xml')
# result = tagger.tag_text("University of California is located in California, United States")
# print(result)

# def _start_server():
#     call(DEPLOY_SCRIPT)
#
# _start_server()

def tag_named_entities(text):
    tagger = SocketNER(host=NER_SERVER_HOST, port=NER_SERVER_PORT, output_format='inlineXML')
    tagged_text = tagger.tag_text(text)
    tagged_text = '<NER_TAGGED_TEXT>' + tagged_text + '</NER_TAGGED_TEXT>' # wrap whole doc in this xml tag
    return tagged_text

# if __name__ == "__main__":
#     tag_named_entities()