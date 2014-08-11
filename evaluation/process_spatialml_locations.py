""" Script to process all locations from the stripped SpatialML files and pickle the list of locations in each file
    to a corresponding file in the locations dir.
"""

import os
import re
import pickle

from bs4 import BeautifulSoup, NavigableString

from models import CorpusLocation, Coordinate
import utilities
import config

# regexes to match latLong attribute values as in SpatialML in both standard and an alternate form
LATLONG_REGEX_STANDARD = re.compile(r"""
                                    ^[^\d]*             # any leading junk
                                    (\d+\.\d+)          # latitude
                                    [^\d°]*             # any junk here
                                    °                   # degree sign
                                    ([NS])              # north or south
                                    \s+                 # space between lat and long
                                    ([\d]+\.[\d]+)      # longitude
                                    [^\d°]*             # any junk here
                                    °                   # degree sign
                                    ([EW])              # east or west
                                    [^\d]*$             # any trailing junk
                                    """, re.VERBOSE)

LATLONG_REGEX_ALTERNATE = re.compile(r"""
                                     ^[^\d]*            # any leading junk
                                     (-?\d+\.\d+)       # latitude
                                     \s*                # any space here
                                     ,?                 # comma sometimes here
                                     \s*                # any space here
                                     (-?\d+\.\d+)       # longitude
                                     [^\d]*$            # any trailing junk
                                     """, re.VERBOSE)

def process_spatialml_locations():
    """ Main logic of script - process all stripped SpatialML files to extract a list of location objects from each
        and pickle this to corresponding file in the locations dir.
    """

    for spatialml_file in os.listdir(config.SPATIALML_SIMPLE_DIR):

        print("Processing {}...".format(spatialml_file))

        # extract all locations in file
        locations = get_locations_from_spatialml(spatialml_file)

        # for location in locations:
        #     print(location)

        # pickle list to corresponding file in locations dir
        with open(config.SPATIALML_SIMPLE_LOCATIONS_DIR + spatialml_file, 'wb') as pickle_file:
            pickle.dump(locations, pickle_file)


def get_locations_from_spatialml(spatialml_file):
    """ Process all place tags from some stripped SpatialML text (as obtained using strip_spatialml.py) into a list
    of location objects.
    """

    # process the spatial_ml text as xml
    spatialml_text = utilities.read_from_file(config.SPATIALML_SIMPLE_DIR + spatialml_file)
    soup = BeautifulSoup(spatialml_text, 'xml')

    # iterate through all the child elements of the SpatialML tag (both Tags and NavigableStrings) keeping track of
    # non-tag chars covered
    chars_processed = 0
    locations = []
    for child in soup.find('SpatialML').children:

        # if reach a place tag process this as a CorpusLocation
        if child.name == 'PLACE':

            gazref = child['gazref'] if child.has_attr('gazref') else None
            name = child.string
            coordinate = process_latLong(child['latLong'], spatialml_file) if child.has_attr('latLong') else None
            country = child['country']  if child.has_attr('country') else None

            # id = child['id'] # not needed I think

            start = chars_processed
            chars_processed += len(child.string)
            stop = chars_processed

            # add new location to list
            new_loc = CorpusLocation(name, start, stop, gazref, country, coordinate)
            locations.append(new_loc)

        # otherwise just add length of the string to the chars processed
        elif isinstance(child, NavigableString):
            chars_processed += len(child)

        # should only be place tags or NavigableStrings as children so raise error
        else:
            raise Exception("Something went wrong...")

    return locations

def process_latLong(latLong, spatialml_file):
    """ Process a latitute and longitude as given in a SpatialML latLong attribute into a Coordinate object. """

    # try to match latLong against standard format
    match = LATLONG_REGEX_STANDARD.match(latLong)

    # if matches standard format parse the lat and long
    if match:
        # assign latitude and longitude depending on match
        lat = float(match.group(1))
        if match.group(2) == 'S':
            lat = -lat

        long = float(match.group(3))
        if match.group(4) == 'W':
            long = -long

    # otherwise try to match against different format used sometimes
    else:
        match = LATLONG_REGEX_ALTERNATE.match(latLong)

        if match:
            lat = match.group(1)
            long = match.group(2)
        else:
            print("ALERT: latLong did not match - latLong = ({}), file = ({})".format(latLong, spatialml_file))
            return None

    # return resulting coordinate (coord args in order (long, lat) to match order used in KML)
    return Coordinate(long, lat)

if __name__ == '__main__':
    # print(process_latLong("36.000°N 138.000°E", None))
    # print(process_latLong("11.000, -12.130", None))

    process_spatialml_locations()