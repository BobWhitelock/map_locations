import re

from bs4 import BeautifulSoup, NavigableString
from identification import identify
from models import Coordinate, CorpusLocation, IGDBEntry

from corenlp_interface import corenlp_tag_text
from utilities import read_from_file
from config import SPATIALML_RAW_DIR, SPATIALML_SIMPLE_DIR

def evaluate():
    # for each original file in the SpatialML corpus
        # read the content
        # tag the named entities
        # identify the named intities

        # extract the identified locations from corresponding file in simplified corpus

    pass

def evaluate_identified_locs_against_corpus_locs(identified_locations, corpus_locations):

    equiv_distance = 50

    # calculate recognition and disambiguation precision (proportion of retrieved values that are relevant i.e.
    # proportion of identified locations that are also in the corpus locations)

    recog_precision_count = 0
    disambig_precision_count = 0

    # for each identified location
    for ided_loc in identified_locations:
        ided_loc_starts = ided_loc.named_location.positions
        for start_pos in ided_loc_starts:

            # see if same area has been marked as a place in the corpus locations
            for corp_loc in corpus_locations:
                stop_pos = ided_loc_starts[start_pos]

                print("\nided_loc_start: ", start_pos, "corp_loc_start: ", corp_loc.start)
                print("ided_loc_end: ", stop_pos, "corp_loc_end: ", corp_loc.stop)

                if corp_loc.start == start_pos and corp_loc.stop == stop_pos:
                # if so increment recognition count and see if can consider identified locations equivalent
                    recog_precision_count += 1
                    # if equivalent increment disambiguation count
                    ided_coords = ided_loc.identified_geoname.coordinates
                    corp_coords = corp_loc.gazetteer_entry.coordinates

                    if ided_coords is not None and corp_coords is not None:
                        if ided_coords.distance_to(corp_coords) < equiv_distance:
                            disambig_precision_count += 1
                    else:
                        print("TODO deal with properly")

                print("\n")

    # print(recog_precision_count)
    # print(disambig_precision_count)

    # calculate recognition and disambiguation precisions
    total_ided_locs = len(identified_locations)
    recog_precision = recog_precision_count / total_ided_locs
    disambig_precision = disambig_precision_count / total_ided_locs

    print("recog: ", recog_precision)
    print("disambig: ", disambig_precision)

    # calculate recognition and disambiguation recall (proportion of relevant values retrieved i.e. proportion of corpus
    # locations found)

    # for each corpus location
        # see if same area has been identified as a location in identified locations
            # if so increment recognition count and see if can consider identified locations equivalent
                # if equivalent increment disambiguation count

def get_locations_from_spatialml(spatialml_text):

    # process the spatial_ml as xml
    soup = BeautifulSoup(spatialml_text, 'xml')

    # iterate through all the child elements of the SpatialML tag (both Tags and NavigableStrings) keeping track of
    # non-tag chars covered
    chars_processed = 0
    locations = []
    for child in soup.find('SpatialML').children:

        # if reach a place tag process this as a CorpusLocation
        if child.name == 'PLACE':
            print(child)

            gazref = child['gazref']
            name = child.string
            coordinates = process_latLong(child['latLong']) if child.has_attr('latLong') else None
            country = child['country']

            id = child['id']

            start = chars_processed
            chars_processed += len(child.string)
            stop = chars_processed
            #
            # # if already exists location with this id add new positions to this
            # for location in locations:
            #     if location.id == id:
            #         location.add_position(start, stop)
            #         continue

            # otherwise add new location to list
            new_igdb_entry = IGDBEntry(gazref, name, country, coordinates)
            new_loc = CorpusLocation(name, id, start, stop, new_igdb_entry)
            locations.append(new_loc)

        # otherwise just add length of the string to the chars processed
        elif isinstance(child, NavigableString):
            chars_processed += len(child)

        # should only be place tags or NavigableStrings as children so raise error
        else:
            raise Exception("Something went wrong...")

    return locations

# def equivalent(corpus)

def process_latLong(latLong):
    """ Process a latitute and longitude as given in a SpatialML latLong attribute as a Coordinate object. """

    # extract parts of latLong string
    latLongRegex = '^\\s*([\\d]+\\.[\\d]+)°([NS])\\s+([\\d]+\\.[\\d]+)°([EW])\\s*$'
    pattern = re.compile(latLongRegex)
    match = pattern.match(latLong)

    # assign latitude and longitude depending on match and return as a Coordinate
    lat = float(match.group(1))
    if match.group(2) == 'S':
        lat = -lat

    long = float(match.group(3))
    if match.group(4) == 'W':
        long = -long

    return Coordinate(long, lat)

def main():
    # locs = get_locations_from_spatialml(read_from_file('spatialml_simple/AFP_ENG_20030401.0476.sgm.dtdvalidated'))
    # for loc in locs:
    #     print(loc)

    test_file = "AFP_ENG_20030330.0211.sgm.dtdvalidated"
    content = read_from_file(SPATIALML_RAW_DIR + test_file)
    tagged = corenlp_tag_text(content)
    ided_locs = identify(tagged)


    for ided_loc in ided_locs:
        for pos in ided_loc.named_location.positions:
            print("start: ", pos, "end: ", ided_loc.named_location.positions[pos])

    corp_locs = get_locations_from_spatialml(read_from_file(SPATIALML_SIMPLE_DIR + test_file))

    for corp_loc in corp_locs:
        print("start: ", corp_loc.start, "stop: ", corp_loc.stop)

    evaluate_identified_locs_against_corpus_locs(ided_locs, corp_locs)


if __name__ == '__main__':
    main()