#!/usr/bin/env python3

""" Module deals with the disambiguation of locations given text where locations (and other features) have been
    identified and marked up.
"""

# Note: both calling GeoNames API directly or (even more so) through GeoPy API does not give enough info, need to use DB

from operator import attrgetter

import mysql.connector
from bs4 import BeautifulSoup

from config import MYSQL_HOST, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DATABASE


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
class Location:
    """ Represents any geographical location. """

    def __init__(self, name, country_code, latitude, longitude, altitude, population):
        self.name = name
        self.country_code = country_code
        self.coordinates = Coordinate(latitude, longitude, altitude)
        self.population = population

    def __str__(self):
        string_rep = "{0} ({1}), ({2}), population: {3}".format(self.name, self.country_code, self.coordinates, self.population)
        return string_rep


def _extract_locations(tagged_text):
    """ Given text marked up by with 'location' tags, as given by the named_entity_recognition module, return
        a list of the locations given by all such tags.
    """

    soup = BeautifulSoup(tagged_text, 'xml')
    locations = [tag.text for tag in soup.find_all('LOCATION')]
    return locations

def _find_candidates(location_name):
    """ Find all candidate locations in database for this name. """

    # create database connection
    connection = mysql.connector.Connect(user=MYSQL_USERNAME, password=MYSQL_PASSWORD, host=MYSQL_HOST, database=MYSQL_DATABASE)
    cursor = connection.cursor()


    # TODO should search alternate_names table and add associated geoname if found
    # - most countries are referred to not by their full name but an alternative so this will cover them

    # countries_query = "SELECT name, geonameid FROM countryinfo WHERE name = {}".format(location_name)
    # cursor.execute(countries_query)

    geoname_query = "SELECT name, country_code, latitude, longitude, elevation, population FROM geoname WHERE name = '{}'".format(location_name)
    cursor.execute(geoname_query)

    list_of_candidates = []
    for (name, country_code, latitude, longitude, elevation, population) in cursor:
        geoname = Location(name, country_code, latitude, longitude, elevation, population)
        list_of_candidates.append(geoname)

    cursor.close()
    connection.close()

    return list_of_candidates

# temp way to find best candidate - just pick with most population
def geoname_with_highest_population(list_of_candidates):
    return max(list_of_candidates, key=attrgetter('population'))

def disambiguate(candidates):
    pass

# testing
def main():
    list_of_candidates = _find_candidates('Sheffield')
    print(str(len(list_of_candidates)) + " candidates")
    top_candidate = geoname_with_highest_population(list_of_candidates)
    print(top_candidate)

if __name__ == '__main__':
    main()