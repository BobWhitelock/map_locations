import os
import pickle

from config import SPATIALML_SIMPLE_DIR, SPATIALML_SIMPLE_LOCATIONS_DIR, SPATIALML_IDENTIFIED_LOCATIONS_HIGHEST_POP_DIR


def main():

    # create overall lists containing the list of locations for each file for both the identified locations and the
    # gold standard, by unpickling the previously pickled files
    list_of_lists_of_identified_locs = []
    list_of_lists_of_gold_standard_locs = []
    for spatialml_file in os.listdir(SPATIALML_SIMPLE_DIR):
        print("Unpickling locations from {}...".format(spatialml_file))

        with open(SPATIALML_IDENTIFIED_LOCATIONS_HIGHEST_POP_DIR + spatialml_file, 'rb') as pickled_file:
            list_of_lists_of_identified_locs.append(pickle.load(pickled_file))

        with open(SPATIALML_SIMPLE_LOCATIONS_DIR + spatialml_file, 'rb') as pickled_file:
            list_of_lists_of_gold_standard_locs.append(pickle.load(pickled_file))

    assert len(list_of_lists_of_identified_locs) == len(list_of_lists_of_gold_standard_locs), "length of lists should be equal"
    
    calculate_micro_average_f_measures(list_of_lists_of_identified_locs, list_of_lists_of_gold_standard_locs)


def calculate_micro_average_f_measures(list_of_lists_of_identified_locs, list_of_lists_of_gold_standard_locs):

    recog_true_positives = 0
    recog_false_positives = 0
    recog_false_negatives = 0

    recognised_locs = {}

    # for each corresponding list of locations
    for index in range(len(list_of_lists_of_identified_locs)):
        current_ided_locs = list_of_lists_of_identified_locs[index]
        current_gold_standard_locs = list_of_lists_of_gold_standard_locs[index]

        # add to sums of true positives, false positives, and false negatives for recognition
        for ided_loc in current_ided_locs:
            for gold_standard_loc in current_gold_standard_locs:
                if consider_equal_references(ided_loc, gold_standard_loc):
                    recog_true_positives += 1
                    if gold_standard_loc.coordinate and ided_loc.identified_geoname:
                        recognised_locs[ided_loc] = gold_standard_loc
                    break
            else:
                recog_false_positives += 1

        for gold_standard_loc in current_gold_standard_locs:
            if gold_standard_loc not in current_ided_locs:
                recog_false_negatives += 1


    # calculate micro-average precision = sum(true positives) / sum(total positives)
    recog_precision = recog_true_positives / (recog_true_positives + recog_false_positives)

    # calculate micro-average recall = sum(true positives) / sum(true positives + false negatives)
    recog_recall = recog_true_positives / (recog_true_positives + recog_false_negatives)

    # calculate micro-average F-measure = harmonic mean of precision and recall
    recog_f_measure = harmonic_mean(recog_precision, recog_recall)

    # calculate disambiguation precision from just recognised locations (recall not relevant)
    disambig_true_positives = 0
    disambig_false_positives = 0

    for recognised_loc in recognised_locs:
        actual_loc = recognised_locs[recognised_loc]

        if consider_identified_same(recognised_loc, actual_loc, 100):
            disambig_true_positives += 1
        else:
            disambig_false_positives += 1

    disambig_precision = disambig_true_positives / (disambig_true_positives + disambig_false_positives)

    # output results
    print("\n")

    print("Recognition")
    print("precision:", recog_precision)
    print("recall:", recog_recall)
    print("F-measure:", recog_f_measure)

    print("\n")

    print("Disambiguation")
    print("precision:", disambig_precision)

    print("\n")

def harmonic_mean(precision, recall):
    return (2 * precision * recall) / (precision + recall)


def consider_equal_references(candidate_loc_ref, actual_loc_ref):
    """ Return boolean value of whether can consider locational references to be the same; this is True if and only
        if they occupy the exact same area.
    """

    if candidate_loc_ref.start == actual_loc_ref.start and candidate_loc_ref.stop == actual_loc_ref.stop:
        return True
    else:
        return False


def consider_identified_same(identified_loc, actual_loc, distance_threshold):
    """ Return boolean value of whether can consider the two locations to be identified as the same location. For
        this to be True they must have the same name and coordinates within the given distance threshold.
    """

    if identified_loc.name == actual_loc.name and \
            identified_loc.coordinate.distance_to(actual_loc.coordinate) <= distance_threshold:
        return True
    else:
        return False

if __name__ == '__main__':
    main()