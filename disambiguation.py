#!/usr/bin/env python3

""" Module deals with the identification and disambiguation of locations given text where locations (and other features)
    have been identified and marked up.
"""

# Note: both calling GeoNames API directly or (even more so) through GeoPy API does not give enough info, need to use DB

# TODO rename module as fulfils more than just disambiguation?

from operator import attrgetter

from bs4 import BeautifulSoup

from models import IdentifiedLocation, NamedLocation
from utilities import form_filename


def _extract_locations(tagged_text):
    """ Given text marked up by with 'location' tags, as given by the named_entity_recognition module, return
        a list of the location names given by all such tags (as NamedLocation objects).
    """

    soup = BeautifulSoup(tagged_text, 'xml')

    # extract sequences of LOCATION-identified tokens from xml as NamedLocation objects
    named_locations = []
    for sentence in soup.find_all('sentence'):
        current_location_tokens = []  # list of tokens in location currently capturing
        for token in sentence.find_all('token'):
            ne_type = token.NER.string

            # if token is LOCATION add to list for location currently capturing
            if ne_type == "LOCATION":
                current_location_tokens.append(token)

            # otherwise if have captured location form a NamedLocation and store, or update existing NamedLocation
            # with same name
            elif len(current_location_tokens) > 0:
                named_location = NamedLocation(sentence, current_location_tokens)

                if named_location in named_locations:
                    named_locations[named_locations.index(named_location)].add_sentence(sentence)
                else:
                    named_locations.append(named_location)

                # reset list of captured tokens
                current_location_tokens = []

        # if trailing location at end of sentence something has gone wrong (as sentence should end with '.'
        if len(current_location_tokens) > 0:
            # TODO more error handling?
            raise Exception("ERROR in _extract_locations()")

    return named_locations

# temp way to find best candidate - just pick with most population
def highest_population_disambiguation(named_location):
    if len(named_location.candidates) > 0:
        top_candidate = max(named_location.candidates, key=attrgetter('population'))
    else:
        top_candidate = None

    return IdentifiedLocation(named_location, top_candidate)


def disambiguate(ne_tagged_text, candidates_dir):
    """ Identify the most likely candidate, if any, for each marked location in the given text with named entities
        identified, and return the list of found locations. For each location the list of candidates will be written
        to a file in the given directory.
    """

    identified_locations = []

    # extract all locations from tagged text and find most likely candidate for each
    named_locations = _extract_locations(ne_tagged_text)
    for named_location in named_locations:

        print("Identifying candidate locations for '{}'...".format(named_location.name))
        named_location.find_candidates()

        # TODO refactor to method of NamedLocation?
        # write all candidates to a file
        location_filename = candidates_dir + form_filename(named_location.name)
        location_file = open(location_filename, 'w')
        location_file.write(named_location.name + '\n')
        location_file.write('\n')
        for candidate in named_location.candidates:
            location_file.write(str(candidate) + '\n')

        print("{} candidate locations identified and written to {}.".format(len(named_location.candidates),
                                                                            location_filename))

        # identify most likely candidate (just based on population) if any and add to list
        print("Identifying most likely candidate...")
        identified_location = highest_population_disambiguation(named_location)
        identified_locations.append(identified_location)
        print("'{}' identified as '{}'.".format(named_location.name, identified_location.identified_geoname))

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