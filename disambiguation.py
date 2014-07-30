#!/usr/bin/env python3

""" Module deals with the identification and disambiguation of locations given text where locations (and other features)
    have been identified and marked up.
"""

# Note: both calling GeoNames API directly or (even more so) through GeoPy API does not give enough info, need to use DB

from operator import attrgetter

from bs4 import BeautifulSoup

from models import NamedLocation, IdentifiedLocation
from utilities import form_filename


def _extract_locations(tagged_text):
    """ Given text marked up by with 'location' tags, as given by the named_entity_recognition module, return
        a list of the location names given by all such tags (as NamedLocation objects).
    """

    # temp while using NER server not CoreNLP
    if not tagged_text.startswith("<NE_TAGGED_TEXT>"):
        tagged_text = "<NE_TAGGED_TEXT>" + tagged_text + "<NE_TAGGED_TEXT>"

    soup = BeautifulSoup(tagged_text, 'xml')
    named_locations = [NamedLocation(name) for name in [tag.text for tag in soup.find_all('LOCATION')]]

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
        print("'{}' identified as '{}'.".format(named_location, identified_location.identified_geoname))

    return identified_locations


# def identify_most_likely_location(location_name):
#     candidates = _find_candidates(location_name)
#     return disambiguate(candidates)


# testing
def main():
    locs = _extract_locations(open("results/Crashes_mount_as_military_flies_more_drones_in_US/02_ne_tagged.xml").read())
    for loc in locs:
        print(loc.name)

if __name__ == '__main__':
    main()