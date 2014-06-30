#!/usr/bin/env python3

import mysql.connector
import lxml
from operator import attrgetter
from config import MYSQL_HOST, MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_DATABASE
from bs4 import BeautifulSoup

# Note: both calling GeoNames API directly or (even more so) through GeoPy API does not give enough info, need to use DB

# represents a geoname as given in the db - TODO flesh out - store code as country? - lat, long as point?
class Geoname:

    def __init__(self, name, country_code, latitude, longitude, population):
        self.name = name
        self.country_code = country_code
        self.latitude = latitude
        self.longitude = longitude
        self.population = population

    def __str__(self):
        string_rep = "{0} ({1}), ({2}, {3}), population: {4}".format(self.name, self.country_code,
                                                                     self.latitude, self.longitude, self.population)
        return string_rep

# get list of all locations identified in named entity tagged text (LOCATION tags)
# TODO improve design - this probably shouldn't go here
def extract_locations(tagged_text):
    soup = BeautifulSoup(tagged_text, 'xml')
    locations = [tag.text for tag in soup.find_all('LOCATION')]
    return locations

# temp way to find best candidate - just pick with most population
def geoname_with_highest_population(list_of_candidates):
    return max(list_of_candidates, key=attrgetter('population'))

# get list of all geoname candidates in db
def find_candidates(location_name):
    connection = mysql.connector.Connect(user=MYSQL_USERNAME, password=MYSQL_PASSWORD, host=MYSQL_HOST, database=MYSQL_DATABASE)

    query = "SELECT name, country_code, latitude, longitude, population FROM geoname WHERE name = '{}';".format(location_name)
    cursor = connection.cursor()
    cursor.execute(query)

    list_of_candidates = []
    for (name, country_code, latitude, longitude, population) in cursor:
        geoname = Geoname(name, country_code, latitude, longitude, population)
        list_of_candidates.append(geoname)

    cursor.close()
    connection.close()

    return list_of_candidates

# testing
def main():
    list_of_candidates = find_candidates('Sheffield')
    print(str(len(list_of_candidates)) + " candidates")
    top_candidate = geoname_with_highest_population(list_of_candidates)
    print(top_candidate)

if __name__ == '__main__':
    main()