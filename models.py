import mysql.connector

from config import MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DATABASE


class NamedLocation:
    """ Represents a location name identified from some text, and associated information. """

    def __init__(self, sentence, tokens):
        self.name = ' '.join([token.word.string for token in tokens])
        self.candidates = []
        self.sentences = [sentence]

    def __str__(self):
        # TODO add more fields
        return "NamedLocation (name={})".format(self.name)

    def __eq__(self, other):
        if self.name == other.name:
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def add_sentence(self, sentence):
        self.sentences.append(sentence)

        # TODO add more details to geonames when add to candidates
    def find_candidates(self):
        """ Find all candidate locations in database for this name. """

        candidates = []

        # create database connection
        connection = mysql.connector.Connect(user=MYSQL_USERNAME, password=MYSQL_PASSWORD, host=MYSQL_HOST,
                                             database=MYSQL_DATABASE)
        cursor = connection.cursor()

        # search geoname table for matches and add all to candidates - note wrap inner query with outer query to only
        # select exact name matches (do this way rather than all in one to make use of existing db index - could add new
        # index)
        geoname_query = "SELECT geonameid, name, country_code, latitude, longitude, elevation, population " \
                        "FROM " \
                        "geoname WHERE name = '{0}'".format(self.name)
        cursor.execute(geoname_query)
        for (geonameid, name, country_code, latitude, longitude, elevation, population) in cursor:
            geoname = Geoname(geonameid, name, country_code, latitude, longitude, elevation, population)
            candidates.append(geoname)

        # search alternate_names table for matches - wrap inner query to select exact name matches as for above query
        # alternate_names_query = "SELECT geonameid " \
        #                         "FROM " \
        #                         "(SELECT * FROM alternate_names WHERE alternate_name = '{0}') AS temp " \
        #                         "WHERE BINARY alternate_name = '{0}'".format(self.name)
        alternate_names_query = "SELECT geonameid " \
                                "FROM " \
                                " alternate_names WHERE alternate_name = '{0}'".format(self.name)
        cursor.execute(alternate_names_query)

        # identify unique newly found geonames using their geonameids
        unique_found_ids = [geonameid for geonameid in set([geonameid for (geonameid,) in cursor])]
        new_ids = [geonameid for geonameid in unique_found_ids if geonameid not in
                   [candidate.geonameid for candidate in candidates]]

        # find and add corresponding locations for these ids to list of candidates
        for geonameid in new_ids:
            geonameid_query = "SELECT geonameid, name, country_code, latitude, longitude, elevation, population " \
                              "FROM geoname WHERE geonameid = '{}'".format(geonameid)
            cursor.execute(geonameid_query)
            for (geonameid, name, country_code, latitude, longitude, elevation, population) in cursor:
                geoname = Geoname(geonameid, name, country_code, latitude, longitude, elevation, population)
                candidates.append(geoname)

        # close database connection
        cursor.close()
        connection.close()

        self.candidates = candidates

class Geoname:
    """ Represents a geoname as given in the geoname table of the geonames database. """

    def __init__(self, geonameid, name, country_code, latitude, longitude, altitude, population):
        self.geonameid = geonameid
        self.name = name
        self.country_code = country_code
        self.coordinates = Coordinate(longitude, latitude, altitude)
        self.population = population

    def __str__(self):
        # string_rep = "{}, {} ({}), ({}), population: {}".format(self.geonameid, self.name, self.country_code,
        # self.coordinates, self.population)

        return "Geoname (geonameid={}, name={}, country={}, coordinates={}, population={})" \
            .format(self.geonameid, self.name, self.country_code, self.coordinates, self.population)

    def __repr__(self):
        return self.__str__()


class IdentifiedLocation:

    def __init__(self, named_location, identified_geoname):
        self.named_location = named_location
        self.identified_geoname = identified_geoname

    def __str__(self):
        return "IdentifiedLocation (named_location={}, identified_location={})".format(self.named_location,
                                                                                       self.identified_geoname)


class Coordinate:
    """ Represents a position on the Earth's surface (longitude, latitude, altitude (optional)) """

    # altitude defaults to None not 0 to not imply position at sea level if don't know where it is
    def __init__(self, longitude, latitude, altitude=None):
        # if self._valid_longitude(longitude):
        # self.longitude = longitude
        # else:
        #     raise ValueError("Invalid longitude value {} given.".format(longitude))
        #
        # if self._valid_latitude(latitude):
        #     self.latitude = latitude
        # else:
        #     raise ValueError("Invalid latitude value {} given.".format(latitude))

        self.longitude = longitude
        self.latitude = latitude
        self.altitude = altitude # why not elevation? change to?

    # string representation of coordinate as (long, lat, [elevation])
    def __str__(self):
        return "(" + self.as_kml_str() + ")"

    # return string for coordinates as should appear in a Coordinates element of a kml doc
    def as_kml_str(self):
        string_rep = "{}, {}".format(self.longitude, self.latitude)
        if self.altitude is not None:
            string_rep += ", {}".format(self.altitude)
        return string_rep

        # @staticmethod
        # def _valid_longitude(longitude):
        # """ Return whether the given value is of valid type and in the valid range for a longitude value. """
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
