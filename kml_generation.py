""" Module deals with the generation of KML given information about locations. """

import lxml

XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>'
EMPTY_KML_TEXT = '<kml xmlns="http://www.opengis.net/kml/2.2"></kml>'
# EMPTY_KML_ELEMENT = etree.fromstring(EMPTY_KML_TEXT)

def create_placemark(location):
    """ Create a valid KML placemark element given a location. """

    placemark = lxml.etree.Element('Placemark')

    # text for placemark should be name given in text for location + found entry name in gazetteer if this info exists
    try:
        placemark_text = "{} ({})".format(location.name, location.entry_name)
    except AttributeError:
        placemark_text = location.name
    lxml.etree.SubElement(placemark, 'name').text = placemark_text

    # add coordinates to placemark in required format
    point = lxml.etree.SubElement(placemark, 'Point')
    lxml.etree.SubElement(point, 'coordinates').text = str(location.coordinate.as_kml_str())

    return placemark

def create_kml(locations):
    """ Create a valid KML document given a list of locations. """

    kml = lxml.etree.fromstring(EMPTY_KML_TEXT)
    document = lxml.etree.SubElement(kml, 'Document')

    for location in locations:

        # create placemark only if location has some coordinate and name
        if location.coordinate and location.name:
            placemark = create_placemark(location)
            document.append(placemark)

    kml_text = XML_HEADER + lxml.etree.tostring(kml).decode('utf-8')
    return kml_text
