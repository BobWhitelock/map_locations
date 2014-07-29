from nltk.tokenize import sent_tokenize

class NamedLocation:
    """ Represents a location name identified from some text, and associated information. """

    def __init__(self, name, sentence):
        self.name = name
        self.sentences = [sentence]

    def add_sentence(self, sentence):
        self.sentences += sentence


# TODO flesh out - store code as country?
# TODO improve __str__ - if no country code change msg etc
class Geoname:
    """ Represents a geoname as given in the geoname table of the geonames database. """

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


class IdentifiedLocation:
    pass


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
