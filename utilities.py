import re

def form_filename(sentence):
    """ Form a filename representation of a sentence by stripping all non-word chars and replacing whitespace with
        underscores. """

    sentence_stripped = re.sub('[^\w\s]', '', sentence)
    filename = re.sub('[\s]+', '_', sentence_stripped)
    return filename