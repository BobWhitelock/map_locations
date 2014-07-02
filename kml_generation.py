
""" Module deals with the generation of KML given information about locations. """

from lxml import etree

XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>'
EMPTY_KML_TEXT = '<kml xmlns="http://www.opengis.net/kml/2.2"></kml>'
EMPTY_KML_ELEMENT = etree.fromstring(EMPTY_KML_TEXT)

def create_placemark(location):
    """ Create a valid KML placemark element given a Location. """

    placemark = etree.Element('Placemark')
    etree.SubElement(placemark, 'name').text = location.name
    point = etree.SubElement(placemark, 'Point')
    etree.SubElement(point, 'coordinates').text = str(location.coordinates)
    return placemark

def create_kml(locations):
    """ Create a valid KML document given a list of Locations. """

    kml = EMPTY_KML_ELEMENT
    document = etree.SubElement(kml, 'Document')
    for location in locations:
        placemark = create_placemark(location)
        document.append(placemark)

    kml_text = XML_HEADER + etree.tostring(kml).decode('utf-8')
    return kml_text




