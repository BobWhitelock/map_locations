import math
import mysql.connector

from config import MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_DATABASE


class LocationReference:
    """ Represents a location reference identified from some text, and associated information. """

    # TODO add more fields

    def __init__(self, tokens=None):

        # assign attributes based on tokens, tokens can be None so can create a dummy object to inspect
        if tokens is not None:
            self.name = ' '.join([token.word.string for token in tokens])
            self.start = int(tokens[0].CharacterOffsetBegin.string)
            self.stop = int(tokens[-1].CharacterOffsetEnd.string)
        else:
            self.name = None
            self.start = None
            self.stop = None

    def __repr__(self):
        return "LocationReference(name={}, start={}, stop={})".format(self.name, self.start, self.stop)

    # below from NamedLocation

    # def __eq__(self, other):
    #     # return equal if names equal ignoring case as (assume) references to same location
    #     if self.name.upper() == other.name.upper():
    #         return True
    #     else:
    #         return False
    #
    # def __ne__(self, other):
    #     return not self.__eq__(other)

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

        return candidates


class Geoname:

    def __init__(self, geonameid, entry_name, country, latitude, longitude, altitude, population):
        self.geonameid = geonameid
        self.entry_name = entry_name
        self.country = country
        self.coordinate = Coordinate(longitude, latitude, altitude)
        self.population = population

    def __repr__(self):
        # string_rep = "{}, {} ({}), ({}), population: {}".format(self.geonameid, self.name, self.country_code,
        # self.coordinates, self.population)

        return "Geoname(geonameid={}, entry_name={}, country={}, coordinates={}, population={})" \
            .format(self.geonameid, self.entry_name, self.country, self.coordinate, self.population)

class IdentifiedLocation:
    """ Represents a location identified from some text and associated details, including the original recognised
        LocationReference, the candidate Geonames found for this location, and the Geoname identified as this Location.
    """

    def __init__(self, location_reference, candidates, identified_geoname):
        self.location_reference = location_reference
        self.candidates = candidates
        self.identified_geoname = identified_geoname

    def __repr__(self):
        return "IdentifiedLocation(location_reference=({}), identified_geoname=({}), candidates=({}))"\
            .format(self.location_reference, self.identified_geoname, self.candidates)

    def __getattr__(self, attr):
        """ Try to return associated LocationReference's or identified Geoname's value for attribute; if attribute
            does not exist in either then AttributeError will be raised as normal.
        """

        # if a LocationReference attribute (based on examining a dummy LocRef object) return corresponding LocRef's
        # value for it, or None if location_reference is None
        loc_ref_props = vars(LocationReference()).keys()
        if attr in loc_ref_props:
            try:
                return getattr(self.location_reference, attr)
            except AttributeError:
                return None

        # do similar if Geoname attribute
        geoname_props = vars(Geoname(0, 0, 0, 0, 0, 0, 0)).keys()
        if attr in geoname_props:
            try:
                return getattr(self.identified_geoname, attr)
            except AttributeError:
                return None

        # if get here raise AttributeError as normal
        raise AttributeError("%r object has no attribute %r" % (self.__class__, attr))


class CorpusLocation:
    """ Represents a location reference identified from some text by a person and the gazetteer entry identified as
        corresponding to this location. To be used for place tags in the SpatialML corpus.
    """

    def __init__(self, name, start, stop, gazref, country, coordinate):
        self.name = name
        self.start = start
        self.stop = stop
        self.gazref = gazref
        self.country = country
        self.coordinate = coordinate

    def __repr__(self):
        return "CorpusLocation(name={}, start={}, stop={}, gazref={}, country={}, coordinate={})"\
                .format(self.name, self.start, self.stop, self.gazref, self.country, self.coordinate)

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

        # calculate part of calculation inside acos
        inner_calc = (math.sin(math.radians(self.latitude)) * math.sin(math.radians(other.latitude))) \
                     + (math.cos(math.radians(self.latitude)) * math.cos(math.radians(other.latitude))
                        * math.cos(math.radians(self.longitude - other.longitude)))

        # due to floating point errors result may be very slightly above 1 or below -1, but acos only takes values
        # from -1 to 1, so if this happens assign inner_calc to max/min valid argument
        if inner_calc > 1:
            inner_calc = 1
        if inner_calc < -1:
            inner_calc = -1

        # remainder of calculation
        return math.acos(inner_calc) * earth_radius

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
    # c1 = Coordinate(-0.1275, 51.5072) # London
    # c2 = Coordinate(-40.7127, 74.0059) # New York
    # print(c1.distance_to(c2))
    #
    # c1 = Coordinate(600, 500)
    # c2 = Coordinate(600, 500)
    # print(c1.distance_to(c2))

    geo = Geoname(6, "a place", "ZW", 6, 5, 4, 100)
    ided_loc = IdentifiedLocation(None, None, geo)
    print(ided_loc.coordinate)
    print(vars(Geoname(0, 0, 0, 0, 0, 0, 0)).keys())