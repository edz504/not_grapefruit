from initialize import *
from utilities import *
import math
import numpy as np
import pandas as pd
import sys
import time

input_file = ('''/Users/edz/Documents/Princeton/Senior/ORF411'''
              '''/OJ/not_grapefruit/Results/notgrapefruit2016.xlsm''')

# We also need the Results file of the previous year in order to
# initialize the inventory.
last_year_file = ('''/Users/edz/Documents/Princeton/Senior/ORF411'''
                  '''/OJ/not_grapefruit/Results/notgrapefruit2015.xlsm''')

print 'Initializing...'
start = time.time()
initial_inventory = initialize_inventory(last_year_file)
storages, processing_plants, groves, markets, decisions = initialize(
    input_file, initial_inventory)
print 'Initialization took {0}'.format(time.time() - start)

s = storages['S51']
s.add_product('ORA', 500)
assert s.inventory['ORA'] == [500, 0, 0, 0]