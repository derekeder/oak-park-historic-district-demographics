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

table_map = {
    'black': ['P1_004N'],
    'hispanic': ['P2_002N'],
    'white': ['P1_003N'],
    'asian': ['P1_006N'],
    'two+': ['P1_009N'],
    'total': ['P1_001N']
}

header = ['Area'] + sorted(table_map.keys())

writer.writerow(header)

all_areas = districts['features'] + oak_park['features']

for area in all_areas:
    name = area['properties']['NAME']

    # get populations
    population_obj = {}

    for demographic, tables in table_map.items():
        population = 0
        for table in tables:
            census_data = c.pl.geo_block(('NAME', table), area['geometry'], 2020)
            for geo, vals, overlap in census_data:
                population += int(vals[table])
        population_obj.update({demographic: population})

    # write to csv
    row = [name] + [population_obj[demo] for demo in header[1:]]
    writer.writerow(row)
        