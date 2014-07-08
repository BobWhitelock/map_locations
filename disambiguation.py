#!/usr/bin/env python3

""" Module deals with the identification and disambiguation of locations given text where locations (and other features)
    have been identified and marked up.
"""

# Note: both calling GeoNames API directly or (even more so) through GeoPy API does not give enough info, need to use DB

from operator import attrgetter

import mysql.connector
from bs4 import BeautifulSoup

from config import MYSQL_HOST, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DATABASE
from utilities import form_filename


class Coordinate:
    """ Represents a position on the Earth's surface (longitude, latitude, altitude (optional)) """

    # altitude defaults to None not 0 to not imply position at sea level if don't know where it is
    def __init__(self, longitude, latitude, altitude=None):
        # if self._valid_longitude(longitude):
        #     self.longitude = longitude
        # else:
        #     raise ValueError("Invalid longitude value {} given.".format(longitude))
        #
        # if self._valid_latitude(latitude):
        #     self.latitude = latitude
        # else:
        #     raise ValueError("Invalid latitude value {} given.".format(latitude))

        self.longitude = longitude
        self.latitude = latitude
        self.altitude = altitude

    # string representation of coordinate given in same format as in kml
    def __str__(self):
        string_rep = str(self.longitude) + ',' + str(self.latitude)
        if self.altitude is not None:
            string_rep += ',' + str(self.altitude)
        return string_rep

    # @staticmethod
    # def _valid_longitude(longitude):
    #     """ Return whether the given value is of valid type and in the valid range for a longitude value. """
    #
    #     valid_type = isinstance(longitude, Decimal)
    #     valid_range = -180 <= longitude <= 180
    #     return valid_type and valid_range
    #
    # @staticmethod
    # def _valid_latitude(latitude):
    #     """ Return whether the given value is of valid type and in the valid range for a latitude value. """
    #
    #     valid_type = isinstance(latitude, Decimal)
    #     valid_range = -90 <= latitude <= 90
    #     return valid_type and valid_range


# TODO flesh out - store code as country?
# TODO improve __str__ - if no country code change msg etc
class Location:
    """ Represents any geographical location. """

    def __init__(self, geonameid, name, country_code, latitude, longitude, altitude, population):
        self.geonameid = geonameid
        self.name = name
        self.country_code = country_code
        self.coordinates = Coordinate(longitude, latitude, altitude)
        self.population = population

    def __str__(self):
        string_rep = "{}, {} ({}), ({}), population: {}".format(self.geonameid, self.name, self.country_code,
                                                                self.coordinates, self.population)
        return string_rep

    def __repr__(self):
        return self.__str__()


def _extract_locations(tagged_text):
    """ Given text marked up by with 'location' tags, as given by the named_entity_recognition module, return
        a list of the locations given by all such tags.
    """

    soup = BeautifulSoup(tagged_text, 'xml')
    locations = [tag.text for tag in soup.find_all('LOCATION')]
    return locations

def _find_candidates(location_name):
    """ Find all candidate locations in database for this name. """

    candidates = []

    # create database connection
    connection = mysql.connector.Connect(user=MYSQL_USERNAME, password=MYSQL_PASSWORD, host=MYSQL_HOST, database=MYSQL_DATABASE)
    cursor = connection.cursor()

    # search geoname table for matches and add all to candidates - TODO make differentiate accented names
    geoname_query = "SELECT geonameid, name, country_code, latitude, longitude, elevation, population FROM geoname WHERE name = '{}'".format(location_name)
    cursor.execute(geoname_query)
    for (geonameid, name, country_code, latitude, longitude, elevation, population) in cursor:
        geoname = Location(geonameid, name, country_code, latitude, longitude, elevation, population)
        candidates.append(geoname)

    # search alternate_names table for matches
    alternate_names_query = "SELECT geonameid FROM alternate_names WHERE alternate_name = '{}'".format(location_name)
    cursor.execute(alternate_names_query)

    # identify unique newly found geonames using their geonameids
    unique_found_ids = [geonameid for geonameid in set([geonameid for (geonameid,) in cursor])]
    new_ids = [geonameid for geonameid in unique_found_ids if geonameid not in [candidate.geonameid for candidate in candidates]]

    # find and add corresponding locations for these ids to list of candidates
    for geonameid in new_ids:
        geonameid_query = "SELECT geonameid, name, country_code, latitude, longitude, elevation, population FROM geoname WHERE geonameid = '{}'".format(geonameid)
        cursor.execute(geonameid_query)
        for (geonameid, name, country_code, latitude, longitude, elevation, population) in cursor:
            geoname = Location(geonameid, name, country_code, latitude, longitude, elevation, population)
            candidates.append(geoname)

    # close database connection
    cursor.close()
    connection.close()

    return candidates

# temp way to find best candidate - just pick with most population
def _geoname_with_highest_population(candidates):
    return max(candidates, key=attrgetter('population'))

def disambiguate(ne_tagged_text, candidates_dir):
    """ Identify the most likely candidate, if any, for each marked location in the given text with named entities
        identified, and return the list of found locations. For each location the list of candidates will be written
        to a file in the given directory.
    """

    identified_locations = []

    # extract all locations from tagged text and find most likely candidate for each
    location_names = _extract_locations(ne_tagged_text)
    for location_name in location_names:

        print("Identifying candidate locations for '{}'".format(location_name))
        candidates = _find_candidates(location_name)

        # write all candidates to a file
        location_filename = candidates_dir + form_filename(location_name)
        location_file = open(location_filename, 'w')
        location_file.write(location_name + '\n')
        location_file.write('\n')
        for candidate in candidates:
            location_file.write(str(candidate) + '\n')

        print("{} candidate locations identified and written to {}.".format(len(candidates), location_filename))

        # identify most likely candidate (just based on population) if any and add to list
        if len(candidates) > 0:
            print("Identifying most likely candidate...")
            top_candidate = _geoname_with_highest_population(candidates)
            identified_locations.append(top_candidate)
            print("'{}' identified as '{}'.".format(location_name, top_candidate))

    print('\n')

    return identified_locations


# def identify_most_likely_location(location_name):
#     candidates = _find_candidates(location_name)
#     return disambiguate(candidates)


# testing
def main():
    list_of_candidates = _find_candidates('Nepal')
    print(str(len(list_of_candidates)) + " candidates")
    top_candidate = _geoname_with_highest_population(list_of_candidates)
    print(top_candidate)

if __name__ == '__main__':
    main()