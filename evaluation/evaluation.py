import os
import pickle
from collections import defaultdict

import matplotlib.pyplot as plt

import config


DISTANCE_THRESHOLD = 100


class Statistics:

    class FMeasure:
        def __init__(self):
            self.true_positives = 0
            self.false_positives = 0
            self.false_negatives = 0

        def precision(self):
            return self.true_positives / (self.true_positives + self.false_positives)

        def recall(self):
            return self.true_positives / (self.true_positives + self.false_negatives)

        def f_measure(self):
            return (2 * self.precision() * self.recall()) / (self.precision() + self.recall())

    def __init__(self):
        self._disambiguation_successes_per_candidate = defaultdict(lambda: 0)
        self._disambiguation_failures_per_candidate = defaultdict(lambda: 0)

        self.recognition = self.FMeasure()
        self.disambiguation = self.FMeasure()
        self.overall = self.FMeasure()

    def add_disambiguation_success(self, num_candidates):
        self._disambiguation_successes_per_candidate[num_candidates] += 1

    def add_disambiguation_failure(self, num_candidates):
        self._disambiguation_failures_per_candidate[num_candidates] += 1

    def graph(self):
        max_x = max(max(self._disambiguation_successes_per_candidate.keys()),
                    max(self._disambiguation_failures_per_candidate.keys()))

        candidate_successes = []
        candidate_failures = []
        candidate_totals = []
        for num_candidates in range(1, max_x):
            successes = self._disambiguation_successes_per_candidate[num_candidates]
            failures = self._disambiguation_failures_per_candidate[num_candidates]
            candidate_successes.append(successes)
            candidate_failures.append(failures)
            candidate_totals.append(successes + failures)

        plt.plot(range(1, max_x), candidate_successes)
        plt.plot(range(1, max_x), candidate_failures)
        plt.plot(range(1, max_x), candidate_totals)
        plt.show()


def evaluation(identified_locations_dir):
    """ Run full evaluation for locations in given dir, against the gold standard locations. """

    # create overall lists containing the list of locations for each file for both the identified locations and the
    # gold standard, by unpickling the previously pickled files
    list_of_lists_of_identified_locs = []
    list_of_lists_of_gold_standard_locs = []
    for spatialml_file in os.listdir(config.SPATIALML_SIMPLE_DIR): # TODO change dir used to just testing files?
        # print("Unpickling locations from {}...".format(spatialml_file))

        # unpickle locations from specified dir
        with open(identified_locations_dir + spatialml_file, 'rb') as pickled_file:
            list_of_lists_of_identified_locs.append(pickle.load(pickled_file))

        # unpickle gold standard locations
        with open(config.SPATIALML_SIMPLE_LOCATIONS_DIR + spatialml_file, 'rb') as pickled_file:
            list_of_lists_of_gold_standard_locs.append(pickle.load(pickled_file))

    assert len(list_of_lists_of_identified_locs) == len(list_of_lists_of_gold_standard_locs), \
        "length of lists should be equal"
    
    calculate_micro_average_f_measures(list_of_lists_of_identified_locs, list_of_lists_of_gold_standard_locs)


def calculate_micro_average_f_measures(list_of_lists_of_identified_locs, list_of_lists_of_gold_standard_locs):
    """ Calculate the micro-average F-measures for the given overall list of lists of identified locations,
        against the gold standard.
    """

    stats = Statistics()

    # counts of recognition statistics
    # recog_true_positives = 0
    # recog_false_positives = 0
    # recog_false_negatives = 0
    #
    # # counts of overall pipeline statistics
    # overall_true_positives = 0
    # overall_false_positives = 0
    # overall_false_negatives = 0

    # map of recognised locational references to actual, only for those where coordinates for both are identified,
    # to be used for evaluating disambiguation of correctly recognised locations below
    recognised_loc_refs_to_actual = {}

    # define local functions to be used to update the recognition and overall pipeline figures for each pair of
    # identified and gold standard locations for each document
    def update_recognition_figures_for_locs(curr_ided_locs, curr_gold_std_locs, statistics):

        # list of locs in current gold standard locs which have been recognised, so after finding all true positives
        # can identify false negatives
        recognised_gold_standard_locs = []

        # find and add to sums of true and false positives for recognition
        for ided_loc in curr_ided_locs:
            for gold_standard_loc in curr_gold_std_locs:

                # if same reference identified as location in both lists then is a true positive
                if consider_equal_references(ided_loc, gold_standard_loc):
                    statistics.recognition.true_positives += 1
                    recognised_gold_standard_locs.append(gold_standard_loc)

                    # if gold standard location has a coordinate given and location reference found has been
                    # identified with a coordinate, add both to map so can evaluate disambiguation of recognized
                    # locations below
                    if gold_standard_loc.coordinate and ided_loc.identified_geoname and \
                            ided_loc.identified_geoname.coordinate:
                        recognised_loc_refs_to_actual[ided_loc] = gold_standard_loc

                    # break here as have determined is a recognition true positive as same text marked in gold
                    # standard - if this never happens and so break never reached, for-else clause below executes and
                    #  have determined as a recognition false positive
                    break

            # if ided loc not found in the gold standard then is a false positive for recognition
            else:
                statistics.recognition.false_positives += 1

        # add to false negatives for recognition for each gold standard loc not found
        for gold_standard_loc in curr_gold_std_locs:
            if gold_standard_loc not in recognised_gold_standard_locs:
                statistics.recognition.false_negatives += 1

    def update_overall_figures_for_complete_locs(potentially_complete_curr_ided_locs, complete_curr_gold_std_locs,
                                                 statistics):

        # list of locs in current full gold standard locs which have been recognised, so after finding all true
        # positives can identify false negatives
        identified_full_gold_standard_locs = []

        # find and add to sums of true and false positives for overall pipeline
        for ided_loc in potentially_complete_curr_ided_locs:
            for gold_standard_loc in complete_curr_gold_std_locs:

                # for an identified location to be a true positive for full pipeline it must both be identified as a
                # geoname with some coordinate (so comparison can be made), and must match a gold standard location
                # according to both consider_equal_references() and consider_identified_same()
                if ided_loc.identified_geoname and ided_loc.coordinate:
                    if consider_equal_references(ided_loc, gold_standard_loc) and \
                            consider_identified_same(ided_loc, gold_standard_loc, DISTANCE_THRESHOLD):
                                statistics.overall.true_positives += 1
                                identified_full_gold_standard_locs.append(gold_standard_loc)
                                break

            # if an identified location is not determined to be a true positive (so break above never reached),
            # it is a false positive
            else:
                statistics.overall.false_positives += 1

        # add to false negatives for overall pipeline for each gold standard location not found
        for gold_standard_loc in complete_current_gold_standard_locs:
            if gold_standard_loc not in identified_full_gold_standard_locs:
                statistics.overall.false_negatives += 1

    # add to true/false positives/negatives for recognition and the overall pipeline for each document in turn
    for index, current_ided_locs in enumerate(list_of_lists_of_identified_locs):

        # get list of gold standard locs for same document
        current_gold_standard_locs = list_of_lists_of_gold_standard_locs[index]

        # update the recognition figures given the corresponding lists of locations
        update_recognition_figures_for_locs(current_ided_locs, current_gold_standard_locs, stats)

        # Create new lists for those gold standard locations which include coordinates, and for all identified locations
        # minus the ones which correspond to the gold standard locations without coordinates. These are for use in
        # evaluating the full pipeline, we remove corresponding list entries where no gold standard coordinates exist as
        # no way to tell if pipeline has identified these correctly.
        complete_current_gold_standard_locs = [loc for loc in current_gold_standard_locs if loc.coordinate]
        potentially_complete_current_ided_locs = list(current_ided_locs)

        # remove from the potentially complete ided locs if a gold standard loc exists for the same reference which
        # is not complete
        for gold_standard_loc in current_gold_standard_locs:
            if not gold_standard_loc.coordinate:
                for ided_loc in potentially_complete_current_ided_locs:
                    if consider_equal_references(ided_loc, gold_standard_loc):
                        potentially_complete_current_ided_locs.remove(ided_loc)

        # update the overall pipeline figures given the two complete location lists formed above
        update_overall_figures_for_complete_locs(potentially_complete_current_ided_locs,
                                                 complete_current_gold_standard_locs, stats)


    # calculate disambiguation precision from just recognised locations (recall not relevant)
    # TODO change here
    for recognised_loc in recognised_loc_refs_to_actual:
        actual_loc = recognised_loc_refs_to_actual[recognised_loc]

        if consider_identified_same(recognised_loc, actual_loc, DISTANCE_THRESHOLD):
            stats.disambiguation.true_positives += 1
            stats.add_disambiguation_success(len(recognised_loc.candidates))
        else:
            stats.disambiguation.false_positives += 1
            stats.add_disambiguation_failure(len(recognised_loc.candidates))

    # output results
    print("\n")

    print("Recognition")
    print("precision:", stats.recognition.precision())
    print("recall:", stats.recognition.recall())
    print("F-measure:", stats.recognition.f_measure())

    print("\n")

    print("Disambiguation")
    print("precision:", stats.disambiguation.precision())

    print("\n")

    print("Overall")
    print("precision:", stats.overall.precision())
    print("recall:", stats.overall.recall())
    print("F-measure:", stats.overall.f_measure())

    print("\n")

    # print("Disambig successes: ")
    # for numcandidates in sorted(stats.disambiguation_successes_per_candidate.keys()):
    #     print(numcandidates, ": ", stats.disambiguation_successes_per_candidate[numcandidates])
    #
    # print("\nDisambig failures: ")
    # for numcandidates in sorted(stats.disambiguation_failures_per_candidate.keys()):
    #     print(numcandidates, ": ", stats.disambiguation_failures_per_candidate[numcandidates])

    stats.graph()





def recall(true_positives, false_negatives):
    return true_positives / (true_positives + false_negatives)


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
    evaluation(config.SPATIALML_IDENTIFIED_LOCATIONS_HIGHEST_POP_DIR)
    # evaluation(config.SPATIALML_IDENTIFIED_LOCATIONS_RANDOM_DIR)