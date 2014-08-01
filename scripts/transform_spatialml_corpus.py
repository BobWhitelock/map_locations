""" Script to strip out parts of the SpatialML corpus files which my system does not deal with so that an evaluation
    between my system and this "gold standard" can be made. These parts include marking up e.g. 'Japanese' with a PLACE
    tag, the use of LINK etc."""

import os
import bs4
from bs4 import BeautifulSoup
from config import SPATIALML_CORPUS_DIR, SPATIALML_FILE_SUFFIX
from utilities import read_from_file


def main():

    # get paths to all SpatialML files of required format
    all_files = os.listdir(SPATIALML_CORPUS_DIR)
    files_wanted = [file for file in all_files if file.endswith(SPATIALML_FILE_SUFFIX)]

    # TESTING
    files_wanted = [files_wanted[4]]

    # for each file strip unwanted tags and write result to a file with the same name in the simple SpatialML directory
    for filename in files_wanted:

        print(filename)

        content = read_from_file(SPATIALML_CORPUS_DIR + filename)
        soup = BeautifulSoup(content, 'xml')

        # TODO why is finding all children below not finding two elements?

        # for each tag in main SpatialML tag
        for tag in soup.find('SpatialML').children:
            # remove non-PLACE tags (replace with tag content)
            if isinstance(tag, bs4.element.Tag) and tag.name != 'PLACE':
                print("removed:", tag)
                tag.unwrap()
            else:
                print("kept:", tag)


        for tag in soup.find_all('LINK'):
            tag.unwrap()

        print(soup)


            # else:
            #     print(tag, '\n', type(tag))
            # else:
            #     # remove tagged nominal references to places (e.g. 'a town')
            #     if tag.form == 'NOM':
            #         tag.unwrap()
            # print(type(tag))

        # print("***************",soup,"**********************")


    # file = SPATIALML_CORPUS_DIR + files_wanted[0]
    # soup = BeautifulSoup(open(file).read(), 'xml')
    # # print(soup)
    # for el in soup.find("SpatialML").children:
    #     if el.name == 'PLACE':
    #         el.replace_with(el.string)

    # print(soup)
    #
    # print('\n')
    # # soup = BeautifulSoup('<tagitty id="6" />', 'xml')
    # # print(soup)
    # tag = soup.find('LINK')
    # print(type(tag))
    # tag.unwrap()
    # print(soup)

if __name__ == '__main__':
    main()