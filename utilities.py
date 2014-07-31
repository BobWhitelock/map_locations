import re
from datetime import datetime

def form_filename(obj):
    """ Form a filename representation for a given object """

    # if string, strip non-word chars and replace whitespace with underscores
    if isinstance(obj, str):
        sentence_stripped = re.sub('[^\w\s]', '', obj)
        filename = re.sub('[\s]+', '_', sentence_stripped)

    # if datetime, make in format 'yyyy-mm-dd_hh-mm-ss'
    elif isinstance(obj, datetime):
        filename = "{}-{}-{}_{}-{}-{}".format(obj.year, obj.month, obj.day, obj.hour, obj.minute, obj.second)
    return filename

def write_to_file(filepath, text):
    """ Write the given text to a file with the given filepath (overwriting any previous content). """

    with open(filepath, 'w') as file:
        file.write(text)
