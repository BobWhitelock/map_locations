import math
import mysql.connector

from config import MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DATABASE


class NamedLocation:
    """ Represents a location name identified from some text, and associated information. """

    def __init__(self, tokens):
        self.name = ' '.join([token.word.string for token in tokens])

        self.positions = {}
        self.add_position(tokens)

        # self.token_groups = [tokens]

    def __str__(self):
        # TODO add more fields
        return "NamedLocation (name={}, positions={})".format(self.name, self.positions)

    def __eq__(self, other):
        # return equal if names equal ignoring case as (assume) references to same location
        if self.name.upper() == other.name.upper():
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    # def add_token_group(self, tokens):
        # self.token_groups.append(tokens)

    def add_position(self, tokens):
        """ Add the location given by the sequential tokens to the map of positions, by setting the first token's
            start position as a key and the last token's end position as its value.
        """

        self.positions[int(tokens[0].CharacterOffsetBegin.string)] = int(tokens[-1].CharacterOffsetEnd.string)

    # def to_place_tag(self, index):
    #     """ Create a place tag (as a string) for this named location with the given index. """
    #
    #     tag = "<PLACE >


    # def add_sentence(self, sentence):
    #     self.sentences.append(sentence)

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
            geoname = GeonameEntry(geonameid, name, country_code, latitude, longitude, elevation, population)
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
                   [candidate.id for candidate in candidates]]

        # find and add corresponding locations for these ids to list of candidates
        for geonameid in new_ids:
            geonameid_query = "SELECT geonameid, name, country_code, latitude, longitude, elevation, population " \
                              "FROM geoname WHERE geonameid = '{}'".format(geonameid)
            cursor.execute(geonameid_query)
            for (geonameid, name, country_code, latitude, longitude, elevation, population) in cursor:
                geoname = GeonameEntry(geonameid, name, country_code, latitude, longitude, elevation, population)
                candidates.append(geoname)

        # close database connection
        cursor.close()
        connection.close()

        return candidates

class GazetteerEntry:
    """ Represents a single entry in a gazetteer database. """

    def __init__(self, id, name, country_code, latitude, longitude, altitude, population):
        self.id = id
        self.name = name
        self.country_code = country_code
        self.coordinates = Coordinate(longitude, latitude, altitude)
        self.population = population

    def __str__(self):
        # string_rep = "{}, {} ({}), ({}), population: {}".format(self.geonameid, self.name, self.country_code,
        # self.coordinates, self.population)

        return "GazetteerEntry (id={}, name={}, country={}, coordinates={}, population={})" \
            .format(self.id, self.name, self.country_code, self.coordinates, self.population)

    def __repr__(self):
        return self.__str__()


class GeonameEntry(GazetteerEntry):
    """ Represents a geoname as given in the geoname table of the geonames database. """

    def __str__(self):
        return "GeonameEntry (geonameid={}, name={}, country={}, coordinates={}, population={})" \
            .format(self.id, self.name, self.country_code, self.coordinates, self.population)


class IGDBEntry(GazetteerEntry):
    """ Represents an entry in the IGDB gazetteer. """

    def __init__(self, id, name, country_code, coordinates):
        self.id = id
        self.name = name
        self.country_code = country_code
        self.coordinates = coordinates

    def __str__(self):
        return "IGDBEntry (id={}, name={}, country={}, coordinates={})" \
            .format(self.id, self.name, self.country_code, self.coordinates)


class IdentifiedLocation:
    """ Represents a location identified from some text and associated details, including the original recognised
        NamedLocation, the candidate Geonames found for this location, and the Geoname identified as this Location.
    """

    def __init__(self, named_location, candidates, identified_geoname):
        self.named_location = named_location
        self.candidates = candidates
        self.identified_geoname = identified_geoname

    def __str__(self):
        return "IdentifiedLocation (named_location=({}), candidates=({}), identified_geoname=({}))"\
            .format(self.named_location, self.candidates, self.identified_geoname)


class CorpusLocation:
    """ Represents a location reference identified from some text by a person and the gazetteer entry identified as
        corresponding to this location. To be used for place tags in the SpatialML corpus.
    """

    def __init__(self, name, id, start, stop, gazetteer_entry):
        self.name = name
        self.id = id
        self.start = start
        self.stop = stop
        self.gazetteer_entry = gazetteer_entry

    def __str__(self):
        return "CorpusLocation (name={}, id={}, start={}, stop={}, gazetteer_entry={})"\
            .format(self.name, self.id, self.start, self.stop, self.gazetteer_entry)

    # def add_position(self, start, stop):
    #     self.positions[start] = stop


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

        # convert to floats (from decimals as in db) so can use math on - any loss of precision won't matter
        self.longitude = float(longitude)
        self.latitude = float(latitude)
        self.altitude = float(altitude) if altitude is not None else None # why not elevation? change to?

    # string representation of coordinate as (long, lat, [elevation])
    def __str__(self):
        return "(" + self.as_kml_str() + ")"

    # return string for coordinates as should appear in a Coordinates element of a kml doc
    def as_kml_str(self):
        string_rep = "{}, {}".format(self.longitude, self.latitude)
        if self.altitude is not None:
            string_rep += ", {}".format(self.altitude)
        return string_rep

    def distance_to(self, other):
        """ Calculate the distance between this point and another point in km (ignoring altitude).
            See http://janmatuschek.de/LatitudeLongitudeBoundingCoordinates
        """

        earth_radius = 6371

        # print("self:", self)
        # print("other:", other)

        # TODO find why error before when just return acos(..)?

        if self.longitude == other.longitude and self.latitude == other.latitude:
            return 0
        else:
            return math.acos((math.sin(math.radians(self.latitude)) * math.sin(math.radians(other.latitude)))
                            + (math.cos(math.radians(self.latitude)) * math.cos(math.radians(other.latitude))
                            * math.cos(math.radians(self.longitude - other.longitude)))) * earth_radius

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

# testing
if __name__ == '__main__':
    c1 = Coordinate(-0.1275, 51.5072) # London
    c2 = Coordinate(-40.7127, 74.0059) # New York
    print(c1.distance_to(c2))

    c1 = Coordinate(112.5, 2.5)
    c2 = Coordinate(112.5, 2.5)
    print(c1.distance_to(c2))