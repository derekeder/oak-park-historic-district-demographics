import csv
import json
import sys

from census_area import Census

from config import CENSUS_API_KEY

c = Census(CENSUS_API_KEY)

writer = csv.writer(sys.stdout)

with open('data/oak-park-municipal-boundary.geojson', 'r') as f:
    oak_park = json.load(f)
    
with open('data/oak-park-historic-districts.geojson', 'r') as f:
    districts = json.load(f)

table_map_2010 = {
    'black': 'P001004',
    'hispanic': 'P002002',
    'white': 'P001003',
    'asian': 'P001006',
    'two+': 'P001009',
    'total': 'P001001'
}

table_map_2020 = {
    'black': 'P1_004N',
    'hispanic': 'P2_002N',
    'white': 'P1_003N',
    'asian': 'P1_006N',
    'two+': 'P1_009N',
    'total': 'P1_001N'
}

header = ['Area'] + sorted(table_map_2010.keys())

writer.writerow(header)

all_areas = districts['features'] + oak_park['features']

for area in all_areas:
    name = area['properties']['NAME']

    # get populations
    population_obj = {}

    for demographic, table in table_map_2010.items():
        population = 0
        census_data = c.pl.geo_block(('NAME', table), area['geometry'], 2010)
        for geo, vals, overlap in census_data:
            population += int(vals[table])
        population_obj.update({demographic: population})

    # write to csv
    row = [name] + [population_obj[demo] for demo in header[1:]]
    writer.writerow(row)
        