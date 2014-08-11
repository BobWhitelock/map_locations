import re
import datetime

def form_filename(obj):
    """ Form a filename representation for a given object """

    # if string, strip punctuation, take only file part if path given, and replace whitespace with underscores
    if isinstance(obj, str):
        sentence_stripped = re.sub('[^\w\s/]', '', obj)
        file_part = sentence_stripped.split('/')[-1]
        filename = re.sub('[\s]+', '_', file_part)

    # if datetime, make in format 'yyyy-mm-dd_hh-mm-ss'
    elif isinstance(obj, datetime.datetime):
        filename = "{}-{}-{}_{}-{}-{}".format(obj.year, obj.month, obj.day, obj.hour, obj.minute, obj.second)

    return filename

def read_from_file(filepath):
    """ Read all text from the given file. """

    with open(filepath) as file:
        text = file.read()
    return text

def write_to_file(filepath, text):
    """ Write the given text to the given file (overwriting any previous content). """

    with open(filepath, 'w') as file:
        file.write(text)
