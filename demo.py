#!/usr/bin/env python

import csv
import os

from englewood import DotDensityPlotter, mask

INPUT_PATH = 'demo/Wards'
DATA_PATH = 'demo/ward_data.csv'
OUTPUT_PATH = 'demo/output'
MASKS = ['demo/Waterways'] 
MASKED_PATH = 'demo/masked'

# Generate a masked version of the input
print 'Generating masked shapefile.'
mask(INPUT_PATH, MASKED_PATH, MASKS) 

# Get ward data from CSV
# (we could also use data from attributes of the shapefile, a database,
#   or any other data source)
ward_data = csv.DictReader(open(DATA_PATH, 'rU'))

# Convert ward data to a dict with ward numbers as keys
ward_data = dict([(d['ward'], d) for d in ward_data])

def get_data(feature):
    # The third column of the shapefile is the ward number
    ward_id = feature.GetField(2)

    # Get the correct ward data
    try:
        ward = ward_data[ward_id]
        print 'Processing ward "%s"' % ward_id
    except KeyError:
        print 'No data for ward "%s"' % ward_id
        return None

    return {
        'asian': int(ward['nhasian10']),
        'black': int(ward['nhblack10']),
        'hispanic': int(ward['hisp10']),
        'white': int(ward['nhwhite10']),
    }

# Ensure the output path exists
if not os.path.exists(OUTPUT_PATH):
    os.mkdir(OUTPUT_PATH)

# Create a map with one dot for every 25 people of each group
# Each dot will have an attribute 'GROUP' that will be one of
# 'asian', 'black', 'hispanic', or 'white'.
dots = DotDensityPlotter(MASKED_PATH, OUTPUT_PATH, get_data, 25, masks=MASKS)
print 'Beginning plotting'
dots.plot()

