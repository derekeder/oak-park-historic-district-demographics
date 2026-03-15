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

# ACS5 SEX BY AGE (B01001) SUBTABLE DEFINITIONS
#
# RACE/ETHNICITY
# B - Black only
# H - White, not Hispanic
# I - Hispanic
#
# SEX/AGE
# 005 - Boys, ages 10-14
# 006 - Boys, ages 15-17
# 020 - Girls, ages 10-14
# 021 - Girls, ages 15-17

table_map = {
    'black_male': ['B01001B_005E', 'B01001B_006E'],
    'black_female': ['B01001B_020E', 'B01001B_021E'],
    'white_male': ['B01001H_005E', 'B01001H_006E'],
    'white_female': ['B01001H_020E', 'B01001H_021E'],
    'hispanic_male': ['B01001I_005E', 'B01001I_006E'],
    'hispanic_female': ['B01001I_020E', 'B01001I_021E']
}

header = ['Area'] + sorted(table_map.keys())

writer.writerow(header)

# all_areas = districts['features'].append(oak_park['features'])
# print(all_areas)

for area in districts['features']:
    name = area['properties']['NAME']

    # get populations
    population_obj = {}

    for demographic, tables in table_map.items():
        population = 0
        for table in tables:
            acs_data = c.acs5.geo_tract(('NAME', table), area['geometry'])
            for _, tract_data in acs_data:
                population += int(tract_data[table])
        population_obj.update({demographic: population})

    # write to csv
    row = [name] + [population_obj[demo] for demo in header[1:]]
    writer.writerow(row)
        