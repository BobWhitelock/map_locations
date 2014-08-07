""" Module deals with the generation of KML given information about locations. """

from lxml import etree

XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>'
EMPTY_KML_TEXT = '<kml xmlns="http://www.opengis.net/kml/2.2"></kml>'
# EMPTY_KML_ELEMENT = etree.fromstring(EMPTY_KML_TEXT)

def create_placemark(location):
    """ Create a valid KML placemark element given a location. """

    placemark = etree.Element('Placemark')

    # text for placemark should be name given in text for location + found entry name in gazetteer if this info exists
    try:
        placemark_text = "{} ({})".format(location.name, location.entry_name)
    except AttributeError:
        placemark_text = location.name
    etree.SubElement(placemark, 'name').text = placemark_text

    # add coordinates to placemark in required format
    point = etree.SubElement(placemark, 'Point')
    etree.SubElement(point, 'coordinates').text = str(location.coordinate.as_kml_str())

    return placemark

def create_kml(locations):
    """ Create a valid KML document given a list of locations. """

    kml = etree.fromstring(EMPTY_KML_TEXT)
    document = etree.SubElement(kml, 'Document')

    for location in locations:

        # create placemark only if location has some coordinate and name
        if location.coordinate and location.name:
            placemark = create_placemark(location)
            document.append(placemark)

    kml_text = XML_HEADER + etree.tostring(kml).decode('utf-8')
    return kml_text
