from map_locations import map_locations

TEST_URLS = ['http://www.theguardian.com/environment/2014/jul/02/water-key-conflict-iraq-syria-isis',
             'http://www.theguardian.com/world/2014/jun/26/nouri-maliki-admits-syria-air-raids-isis-iraq',
             'http://www.theguardian.com/world/2014/jul/01/ukraine-petro-poroshenko-goes-on-attack',
             'http://www.bbc.co.uk/news/uk-politics-28046590',
             'http://www.bbc.co.uk/news/uk-northern-ireland-28115413',
             'http://www.bbc.co.uk/news/science-environment-28056244',
             'http://www.washingtonpost.com/sf/investigative/2014/06/22/crashes-mount-as-military-flies-more-drones-in-'
             'u-s/',
             'http://www.washingtonpost.com/blogs/capital-weather-gang/wp/2014/07/01/tropical-storm-arthur-forms-foreca'
             'st-to-become-hurricane-on-ride-up-east-coast-july-2-5/?tid=pm_local_pop']

# TEST_URLS = ['http://www.theguardian.com/environment/2014/jul/02/water-key-conflict-iraq-syria-isis',
#              'http://www.bbc.co.uk/news/uk-northern-ireland-28115413']

for url in TEST_URLS:
    map_locations(url=url, display_map=False)