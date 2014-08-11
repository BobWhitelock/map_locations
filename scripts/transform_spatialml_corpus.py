""" Script to strip out parts of the SpatialML corpus files which my system does not deal with so that an evaluation
    between my system and this "gold standard" can be made. These parts include marking up e.g. 'Japanese' with a PLACE
    tag, the use of LINK etc."""

import os
from bs4 import BeautifulSoup
import config
import utilities


def main():

    # get paths to all SpatialML files of required format
    all_files = os.listdir(config.SPATIALML_CORPUS_DIR)
    files_wanted = [file for file in all_files if file.endswith(config.SPATIALML_FILE_SUFFIX)]

    # TESTING
    # files_wanted = [files_wanted[4]]

    # for each file strip unwanted tags and write result to a file with the same name in the simple SpatialML directory
    for filename in files_wanted:

        # parse as xml
        content = utilities.read_from_file(config.SPATIALML_CORPUS_DIR + filename)
        soup = BeautifulSoup(content, 'xml')

        # unwrap all unneeded tags (replace with contents)
        for tag in soup.find_all('LINK') + soup.find_all(('RLINK')) + soup.find_all('SIGNAL'):
            tag.unwrap()

        # unwrap nominal place tags (= tags of nominal references eg. 'city')
        for tag in soup.find_all('PLACE', attrs={'form': 'NOM'}):
            tag.unwrap()

        # unwrap predicative place tags (= tags of e.g. 'Japanese' rather than 'Japan')
        for tag in soup.find_all('PLACE', attrs={'predicative': 'true'}):
            tag.unwrap()

        # write to file with same name in simple SpatialML directory
        utilities.write_to_file(config.SPATIALML_SIMPLE_DIR + filename, str(soup))


if __name__ == '__main__':
    main()