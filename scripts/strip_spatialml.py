""" Script to strip the SpatialML corpus files of all markup so the raw text can be used for evaluation. """

import os
from bs4 import BeautifulSoup
import config
import utilities


def main():

    # get paths to all SpatialML files of required format
    all_files = os.listdir(config.SPATIALML_CORPUS_DIR)
    files_wanted = [file for file in all_files if file.endswith(config.SPATIALML_FILE_SUFFIX)]

    # for each file obtain just the text and write this to a file with the same name in the raw SpatialML directory
    for filename in files_wanted:
        content = utilities.read_from_file(config.SPATIALML_CORPUS_DIR + filename)
        soup = BeautifulSoup(content, 'xml')
        text = soup.get_text()
        utilities.write_to_file(config.SPATIALML_RAW_DIR + filename, text)

if __name__ == '__main__':
    main()