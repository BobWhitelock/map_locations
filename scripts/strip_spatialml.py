""" Script to strip the SpatialML corpus files of all markup so the raw text can be used for evaluation. """

import os
from bs4 import BeautifulSoup
from config import SPATIALML_CORPUS_DIR, SPATIALML_FILE_SUFFIX, SPATIALML_RAW_DIR
from utilities import read_from_file, write_to_file


def main():

    # get paths to all SpatialML files of required format
    all_files = os.listdir(SPATIALML_CORPUS_DIR)
    files_wanted = [file for file in all_files if file.endswith(SPATIALML_FILE_SUFFIX)]

    # for each file obtain just the text and write this to a file with the same name in the raw SpatialML directory
    for filename in files_wanted:
        content = read_from_file(SPATIALML_CORPUS_DIR + filename)
        soup = BeautifulSoup(content, 'xml')
        text = soup.get_text()
        write_to_file(SPATIALML_RAW_DIR + filename, text)

if __name__ == '__main__':
    main()