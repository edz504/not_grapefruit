from initialize import *
from utilities import *
import copy
import math
import numpy as np
import pandas as pd
import subprocess
import sys
import time

# input_file = sys.argv[1]
# last_year_file = sys.argv[2]

# Hard-code the file to use.  Note that we can use both the
# results .xlsm and the original decisions spreadsheet, because
# the results .xlsm contains the decision sheets.
ROOT_DIR = os.path.dirname(os.getcwd())
input_file = os.path.join(ROOT_DIR,
    'decisions/notgrapefruit2019_4test.xlsx')
# input_file = os.path.join(ROOT_DIR,
#     'decisions/notgrapefruit2018.xlsm')

# We also need the Results file of the previous year in order to
# initialize the inventory.
last_year_file = os.path.join(ROOT_DIR,
    'results/notgrapefruit2017.xlsm')

# Hard-code for 4/5 experiment, assume we start with 0 inv
initial_inventory = {
    'S35': {
        'ORA': [0] * 4,
        'POJ': [0] * 8,
        'ROJ': [0] * 12,
        'FCOJ': [0] * 48,
        'XOJ': [0]
    },
    'S51': {
        'ORA': [0] * 4,
        'POJ': [0] * 8,
        'ROJ': [0] * 12,
        'FCOJ': [0] * 48,
        'XOJ': [0]
    },
    'S59': {
        'ORA': [0] * 4,
        'POJ': [0] * 8,
        'ROJ': [0] * 12,
        'FCOJ': [0] * 48,
        'XOJ': [0]
    },
    'S73': {
        'ORA': [0] * 4,
        'POJ': [0] * 8,
        'ROJ': [0] * 12,
        'FCOJ': [0] * 48,
        'XOJ': [0]
    }
}
scheduled_to_ship_in = {
    'S35': {
        'POJ': 98.634,
        'FCOJ': 36.97,
        'ROJ': 45.79196
    },
    'S51': {
        'POJ': 218.88555,
        'FCOJ': 158.05,
        'ROJ': 249.50164,
    },
    'S59': {
        'POJ': 82.316,
        'FCOJ': 77.9730,
        'ROJ': 86.51086
    },
    'S73': {
        'POJ': 122.47359,
        'FCOJ': 101.586,
        'ROJ': 69.24297
    }
}

print 'Initializing...'
start = time.time()
# initial_inventory, scheduled_to_ship_in = initialize_inventory(
#     last_year_file)
storages, processing_plants, groves, markets, decisions = initialize(
    input_file, initial_inventory)
print 'Initialization took {0}'.format(time.time() - start)


# Can easily modify the below to be week by week
sales = {'ORA': 0, 'POJ': 0, 'ROJ': 0, 'FCOJ': 0}
revenues = {'ORA': 0, 'POJ': 0, 'ROJ': 0, 'FCOJ': 0}
cost = {
    'purchase': {
        'raw': 0,
        'futures': {
            'ORA': 0,
            'FCOJ': 0
        }
    },
    'manufacturing': {
        'POJ': 0,
        'FCOJ': 0, 
        'ROJ (reconstitution)': 0
    },
    'transportation': {
        'from_grove': 0,
        'from_plants': 0,
        'from_storages': 0
    },
    'inventory_hold': 0,
    'maintenance': {
        'storage': 0,
        'processing': 0,
        'tanker': 0
    },
    'capacity_change': {
        'storage': 0,
        'processing': 0,
        'tanker': 0
    }
}

leftovers = pd.DataFrame(columns=['t', 'storage', 'product', 'leftover'])

processes = []
deliveries = []
tanker_car_fleets = []

# Add deliveries from scheduled_to_ship_in, arrival week 1
for storage_name, storage in storages.iteritems():
    if storage_name in scheduled_to_ship_in:
        for product, amount in scheduled_to_ship_in[storage_name].iteritems():
            deliveries.append(
                Delivery(sender='prev_year',
                         receiver=storage,
                         arrival_time=1,
                         product=product,
                         amount=amount))

# It seems that when we call add_product on an arriving delivery,
# it modifies the inventory of the other receivers as well??

# Print all storage inventories
for storage in storages.values():
    print storage.inventory

# Select a delivery
delivery = deliveries[0]
print delivery
# Modify its receiver
delivery.receiver.add_product(delivery.product, delivery.amount)

# Check storage inventories
for storage in storages.values():
    print storage.inventory
