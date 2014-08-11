""" Script to run pipeline and identify and disambiguate locations from the raw SpatialMl files, and pickle list of
    locations to a corresponding file.
"""

import os
import pickle

import config
import utilities
import corenlp_interface
import identification

# WARNING: takes quite a few minutes to process all files as need to make request to corenlp server for each file and
# access database multiple times for most files

def identify_spatialml_raw_locations(disambiguation_function, pickled_dir):
    """ Main logic of script - for all raw SpatialML files run pipeline on with given disambiguation function and
        pickle resulting list of locations to a corresponding file in pickled_dir.
    """

    print("Running pipeline on raw SpatialML files using disambiguation function {}...\n"
          .format(disambiguation_function))

    for spatialml_file in os.listdir(config.SPATIALML_RAW_DIR):

        print("Processing {}...".format(spatialml_file))

        # run text in file through pipeline to get list of IdentifiedLocations
        text = utilities.read_from_file(config.SPATIALML_RAW_DIR + spatialml_file)
        corenlp_tagged_text = corenlp_interface.corenlp_tag_text(text)
        locations = identification.identify(corenlp_tagged_text, disambiguation_function)

        # TODO deal with using different disambig methods better
        # pickle locations to corresponding file in corresponding dir
        with open(pickled_dir + spatialml_file, 'wb') as pickle_file:
            pickle.dump(locations, pickle_file)

    print("\n\n")


if __name__ == '__main__':
    # highest population disambiguation
    # identify_spatialml_raw_locations(highest_population_disambiguation, SPATIALML_IDENTIFIED_LOCATIONS_HIGHEST_POP_DIR)

    # random disambiguation
    identify_spatialml_raw_locations(identification.random_disambiguation, config.SPATIALML_IDENTIFIED_LOCATIONS_RANDOM_DIR)