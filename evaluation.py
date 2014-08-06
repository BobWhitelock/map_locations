import re
import os


from bs4 import BeautifulSoup, NavigableString
from identification import identify
from models import Coordinate, CorpusLocation, IGDBEntry

from corenlp_interface import corenlp_tag_text
from utilities import read_from_file
from config import SPATIALML_RAW_DIR, SPATIALML_SIMPLE_DIR

def evaluate():
    # for each original file in the SpatialML corpus
    all_files = os.listdir(SPATIALML_RAW_DIR)

    totals = [0, 0, 0, 0]

    for spatialml_file in all_files:

        print("Evaluating {}...".format(spatialml_file))

        # process file to obtain list of identified locations
        text = read_from_file(SPATIALML_RAW_DIR + spatialml_file)
        corenlp_tagged_text = corenlp_tag_text(text)
        identified_locations = identify(corenlp_tagged_text)

        # extract the "gold standard" locations from corresponding file in simplified corpus
        spatialml = read_from_file(SPATIALML_SIMPLE_DIR + spatialml_file)
        corpus_locations = get_locations_from_spatialml(spatialml)

        # TODO handle better - currently just skip where no matches either way
        if len(identified_locations) > 0 and len(corpus_locations) > 0:
            results = evaluate_identified_locs_against_corpus_locs(identified_locations, corpus_locations)
            for index in range(len(results)):
                totals[index] += results[index]
        else:
            all_files.remove(spatialml_file)

        print(totals)

    num_tests = len(all_files)
    averages = []
    for value in totals:
        averages.append(value / num_tests)

    av_recog_prec = averages[0]
    av_recog_recall = averages[2]
    print(av_recog_prec, av_recog_recall)
    print("Recog F-measure ", harmonic_mean(av_recog_prec, av_recog_recall))

    av_disambig_prec = averages[1]
    av_disambig_recall = averages[3]
    print("Disambig F-measure ", harmonic_mean(av_disambig_prec, av_disambig_recall))


def harmonic_mean(precision, recall):
    return (2 * precision * recall) / (precision + recall)

def evaluate_identified_locs_against_corpus_locs(identified_locations, corpus_locations):

    equiv_distance = 200

    recog_prec, disambig_prec = calculate_precisions(identified_locations, corpus_locations, equiv_distance)
    recog_recall, disambig_recall = calculate_recalls(identified_locations, corpus_locations, equiv_distance)

    return recog_prec, disambig_prec, recog_recall, disambig_recall

    # print(calculate_precisions(identified_locations, corpus_locations, equiv_distance))
    #
    # print(calculate_recalls(identified_locations, corpus_locations, equiv_distance))

def calculate_precisions(identified_locations, corpus_locations, equiv_distance):
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

                # print("\nided_loc_start: ", start_pos, "corp_loc_start: ", corp_loc.start)
                # print("ided_loc_end: ", stop_pos, "corp_loc_end: ", corp_loc.stop)

                if corp_loc.start == start_pos and corp_loc.stop == stop_pos:
                # if so increment recognition count and see if can consider identified locations equivalent
                    recog_precision_count += 1
                    # if equivalent increment disambiguation count
                    if ided_loc.identified_geoname:
                        ided_coords = ided_loc.identified_geoname.coordinates
                        corp_coords = corp_loc.gazetteer_entry.coordinates

                        if ided_coords is not None and corp_coords is not None:
                            if ided_coords.distance_to(corp_coords) < equiv_distance:
                                disambig_precision_count += 1
                        else:
                            print("TODO deal with properly - precision")

                # print("\n")

    # print(recog_precision_count)
    # print(disambig_precision_count)

    # calculate recognition and disambiguation precisions
    total_ided_locs = sum([len(loc.named_location.positions) for loc in identified_locations])
    recog_precision = recog_precision_count / total_ided_locs
    disambig_precision = disambig_precision_count / total_ided_locs

    return recog_precision, disambig_precision

def calculate_recalls(identified_locations, corpus_locations, equiv_distance):
    # calculate recognition and disambiguation recall (proportion of relevant values retrieved i.e. proportion of corpus
    # locations found)

    recog_recall_count = 0
    disambig_recall_count = 0

    # for each corpus location
    for corp_loc in corpus_locations:

        # see if same area has been identified as a location in identified locations
        for ided_loc in identified_locations:
            ided_loc_starts = ided_loc.named_location.positions
            for start_pos in ided_loc_starts:
                stop_pos = ided_loc.named_location.positions[start_pos]

                if corp_loc.start == start_pos and corp_loc.stop == stop_pos:
                    # if so increment recognition count and see if can consider identified locations equivalent
                    recog_recall_count += 1

                    if ided_loc.identified_geoname:
                        ided_coords = ided_loc.identified_geoname.coordinates
                        corp_coords = corp_loc.gazetteer_entry.coordinates

                        # if equivalent increment disambiguation count
                        if ided_coords is not None and corp_coords is not None:
                            if ided_coords.distance_to(corp_coords) < equiv_distance:
                                disambig_recall_count += 1
                        else:
                            print("TODO deal with properly - recall")

    total_corp_locs = len(corpus_locations)
    recog_recall = recog_recall_count / total_corp_locs
    disambig_recall = disambig_recall_count / total_corp_locs

    return recog_recall, disambig_recall

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

            gazref = child['gazref'] if child.has_attr('gazref') else None
            name = child.string
            coordinates = process_latLong(child['latLong']) if child.has_attr('latLong') else None
            country = child['country']  if child.has_attr('country') else None

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
    latLongRegexStandard = '^[^\\d*](\\d+\\.\\d+)[^\\d°]*°([NS])\\s+([\\d]+\\.[\\d]+)[^\\d°]*°([EW])[^\\d*]$'
    pattern = re.compile(latLongRegexStandard)
    match = pattern.match(latLong)

    # if matches standard format parse the lat and long
    if match:
        # assign latitude and longitude depending on match and return as a Coordinate
        lat = float(match.group(1))
        if match.group(2) == 'S':
            lat = -lat

        long = float(match.group(3))
        if match.group(4) == 'W':
            long = -long

    # otherwise try to match against different format used sometimes
    else:
        latLongRegexAlternate = '^\\s*(-?\\d+\\.\\d+)\\s*,?\\s*(-?\\d+\\.\\d+)\\s*$'
        pattern = re.compile(latLongRegexAlternate)
        match = pattern.match(latLong)

        if match:
            lat = match.group(1)
            long = match.group(2)
        else:
            # TODO see if can improve regexes
            return None

    # print(Coordinate(long, lat))

    return Coordinate(long, lat)

def main():
    # # locs = get_locations_from_spatialml(read_from_file('spatialml_simple/AFP_ENG_20030401.0476.sgm.dtdvalidated'))
    # # for loc in locs:
    # #     print(loc)
    #
    # test_file = "AFP_ENG_20030330.0211.sgm.dtdvalidated"
    # content = read_from_file(SPATIALML_RAW_DIR + test_file)
    # tagged = corenlp_tag_text(content)
    # ided_locs = identify(tagged)
    #
    #
    # # for ided_loc in ided_locs:
    # #     print(ided_loc)
    #     # for pos in ided_loc.named_location.positions:
    #     #     print("start: ", pos, "end: ", ided_loc.named_location.positions[pos])
    #
    # corp_locs = get_locations_from_spatialml(read_from_file(SPATIALML_SIMPLE_DIR + test_file))
    #
    # # for corp_loc in corp_locs:
    # #     print(corp_loc)
    #
    # print(evaluate_identified_locs_against_corpus_locs(ided_locs, corp_locs))

    evaluate()

if __name__ == '__main__':
    main()