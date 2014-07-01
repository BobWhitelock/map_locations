# import xml.etree.ElementTree as ET
from lxml import etree

XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>'
EMPTY_KML_TEXT = '<kml xmlns="http://www.opengis.net/kml/2.2"></kml>'
EMPTY_KML_ELEMENT = etree.fromstring(EMPTY_KML_TEXT)


# create valid kml document from a list of locations
def create_kml(locations):
    kml = EMPTY_KML_ELEMENT
    document = etree.SubElement(kml, 'Document')
    for location in locations:
        placemark = create_placemark(location)
        document.append(placemark)

    kml_text = XML_HEADER + str(etree.tostring(kml, pretty_print=True))
    return kml_text

# create a kml placemark tag given a location
def create_placemark(location):
    placemark = etree.Element('Placemark')
    etree.SubElement(placemark, 'name').text = location.name
    point = etree.SubElement(placemark, 'Point')
    etree.SubElement(point, 'coordinates').text = str(location.coordinates)
    return placemark


