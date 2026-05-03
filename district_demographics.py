import csv
import json
import os
import re

from census_area import Census

from config import CENSUS_API_KEY

c = Census(CENSUS_API_KEY)

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

demographics = sorted(table_map_2010.keys())
pct_demos = [d for d in demographics if d != 'total']
header = ['year'] + demographics + [f'{d}_pct' for d in pct_demos]

os.makedirs('data/output', exist_ok=True)

def slugify(name):
    name = name.lower().strip()
    name = re.sub(r'[^a-z0-9]+', '-', name)
    return name.strip('-')

def get_population(geometry, table_map, year):
    population_obj = {}
    for demographic, table in table_map.items():
        population = 0
        census_data = c.pl.geo_block(('NAME', table), geometry, year)
        for geo, vals, overlap in census_data:
            population += int(vals[table])
        population_obj[demographic] = population
    return population_obj

all_areas = districts['features'] + oak_park['features']

for area in all_areas:
    name = area['properties']['NAME']
    filename = f'data/output/{slugify(name)}.csv'

    print(f'Fetching data for {name}...')

    pop_2010 = get_population(area['geometry'], table_map_2010, 2010)
    pop_2020 = get_population(area['geometry'], table_map_2020, 2020)

    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        def pct(pop, d):
            return round(pop[d] / pop['total'] * 100, 1) if pop['total'] else 0

        writer.writerow(header)
        writer.writerow([2010] + [pop_2010[d] for d in demographics] + [pct(pop_2010, d) for d in pct_demos])
        writer.writerow([2020] + [pop_2020[d] for d in demographics] + [pct(pop_2020, d) for d in pct_demos])

    print(f'  Wrote {filename}')
