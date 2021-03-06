#!/usr/bin/env python3

""" Module deals with the identification and disambiguation of locations given text where locations (and other features)
    have been identified and marked up.
"""

# Note: both calling GeoNames API directly or (even more so) through GeoPy API does not give enough info, need to use DB
import os
import random
import operator

from bs4 import BeautifulSoup

from models import IdentifiedLocation, LocationReference
import config
from utilities import form_filename


def _extract_locations(tagged_text):
    """ Given text marked up by with 'location' tags, as given by the named_entity_recognition module, return
        a list of the location names given by all such tags (as LocationReference objects).
    """

    soup = BeautifulSoup(tagged_text, 'xml')

    # extract sequences of LOCATION-identified tokens from xml as NamedLocation objects
    location_references = []
    for sentence in soup.find_all('sentence'):
        current_location_tokens = []  # list of tokens in location currently capturing
        for token in sentence.find_all('token'):
            ne_type = token.NER.string

            # if token is LOCATION add to list for location currently capturing
            if ne_type == "LOCATION":
                current_location_tokens.append(token)

            # otherwise if have captured location form a LocationReference and store
            elif len(current_location_tokens) > 0:
                named_location = LocationReference(current_location_tokens)
                location_references.append(named_location)

                # # if already location with same name update it
                # if named_location in location_references:
                #     location_references[location_references.index(named_location)].add_position(current_location_tokens)
                #
                # # otherwise add a new one
                # else:
                #     location_references.append(named_location)

                # reset list of captured tokens
                current_location_tokens = []

        # if trailing location at end of sentence add it (TODO better currently repeating code)
        if len(current_location_tokens) > 0:
            named_location = LocationReference(current_location_tokens)

            # if already location with same name update it
            if named_location in location_references:
                location_references[location_references.index(named_location)].add_position(current_location_tokens)

            # otherwise add a new one
            else:
                location_references.append(named_location)

    return location_references


def random_disambiguation(candidates):
    if len(candidates) > 0:
        return random.choice(candidates)
    else:
        return None


# temp way to find best candidate - just pick with most population
def highest_population_disambiguation(candidates):
    if len(candidates) > 0:
        return max(candidates, key=operator.attrgetter('population'))
    else:
        return None


# def tag_location(named_location, raw_document):

# def identified_locs_to_xml(identified_locations, tagged_text):
#
#     # for each token in turn in tagged text
#     for token in tagged_text.find_all('token'):
#
#         # if there is a location starting at this position add corresponding place tag starting there
#         for location in identified_locations:
#             for start_position in location.positions:
#                 if start_position == token.CharacterOffsetBegin:
#
#
#             # add all attributes to tag
#             # and skip tokens until reach closing location for place tag
#
#     # unwrap all other tags so just left with places

def identify(ne_tagged_text, results_dir, disambiguation_function=highest_population_disambiguation):
    """ Identify the most likely candidate, if any, for each marked location in the given text with named entities
        identified, and return the list of found locations. For each location the list of candidates will be written
        to a file in the given directory.
    """

    identified_locations = []

    # extract all locations from tagged text and find most likely candidate for each
    location_references = _extract_locations(ne_tagged_text)
    for location_reference in location_references:

        # print("Identifying candidate locations for '{}'...".format(location_reference.name))
        candidates = location_reference.find_candidates()

        # TODO refactor to method of NamedLocation?
        # write all candidates to a file
        candidates_dir =  results_dir + '03_candidates/'
        os.makedirs(candidates_dir, exist_ok=True)
        location_filename = candidates_dir + form_filename(location_reference.name)
        location_file = open(location_filename, 'w')
        location_file.write(location_reference.name + '\n')
        location_file.write('\n')
        for candidate in candidates:
            location_file.write(str(candidate) + '\n')
        #
        # print("{} candidate locations identified and written to {}.".format(len(candidates),
        #                                                                     location_filename))

        # identify most likely candidate (just based on population) if any and add to list
        # print("Identifying most likely candidate...")
        top_candidate = disambiguation_function(candidates)
        identified_location = IdentifiedLocation(location_reference, candidates, top_candidate)
        identified_locations.append(identified_location)
        # print("'{}' identified as '{}'.".format(location_reference.name, identified_location.identified_geoname))

    return identified_locations


# def identify_most_likely_location(location_name):
#     candidates = _find_candidates(location_name)
#     return disambiguate(candidates)


# testing
def main():
    locs = _extract_locations(open("results/Water_supply_key_to_outcome_of_conflicts_in_Iraq_and_Syria_experts_warn/2014-7-31_15-32-32/02_ne_tagged.xml").read())
    for loc in locs:
        print(loc.name)

    for loc in locs:
        if loc.name == 'Iraq':
            print(len(loc.sentences))


if __name__ == '__main__':
    main()