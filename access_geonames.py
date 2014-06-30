#!/usr/bin/env python3

import mysql.connector

# Note: both calling GeoNames API directly or (even more so) through GeoPy API does not give enough info, need to use DB
##############
# from geopy.geocoders import GeoNames
# import requests

# GEONAMES_USERNAME = 'BobWhitelock'
# GEONAMES_SEARCH_URL = 'http://api.geonames.org/search'

#
# def find_candidates(location_name):
#     query_parameters = {'username': GEONAMES_USERNAME,
#                         'name_equals': location_name, # search for exact name, maybe change to just name later?
#                         # - but then many results, but also want to take into account slightly wrong names
#                         'maxRows': 1000}
#     response = requests.get(GEONAMES_SEARCH_URL, params=query_parameters)
#     print(response.text)
################

# find_candidates("London")

def find_candidates(location_name):
    connection = mysql.connector.Connect