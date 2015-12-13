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

#### Test Storage
s = storages['S51']

# Test adding products
s.add_product('ORA', 500)
assert s.inventory['ORA'] == [500, 0, 0, 0]
s.add_product('POJ', 200)
assert s.inventory['POJ'] == [200, 0, 0, 0, 0, 0, 0, 0]

# Test aging
s.age()
assert s.inventory['ORA'] == [0, 500, 0, 0]
assert s.inventory['POJ'] == [0, 200, 0, 0, 0, 0, 0, 0]
s.age()
s.age()
s.age()
assert s.inventory['ORA'] == [0] * 4
assert s.inventory['POJ'] == [0, 0, 0, 0, 200, 0, 0, 0]

# Test inventory totalling
s.add_product('FCOJ', 1000)
s.age()
s.add_product('FCOJ', 1000)
assert s.get_total_inventory('FCOJ') == 2000
assert s.get_total_inventory() == 2200

# Test removing product
s.remove_product('FCOJ', 500)
assert s.inventory['FCOJ'] == [1000, 500] + [0] * 46
s.remove_product('FCOJ', 501)
assert s.inventory['FCOJ'] == [999] + [0] * 47

# Test reconstitution
new_process_list, cost = s.reconstitute(1)
assert s.get_total_inventory('FCOJ') == 819.1800000000001
assert s.get_total_inventory('XOJ') == 179.82
assert cost == 179.82 * 650
assert new_process_list[0].location is s
assert new_process_list[0].start_product == 'FCOJ'
assert new_process_list[0].end_product == 'ROJ'
assert new_process_list[0].finish_time == 2
assert new_process_list[0].amount == 179.82

# Test dispose capacity (Sean, you need to verify this)
t = 2
s.remove_product('XOJ', 179.82)
s.add_product('ROJ', 179.82)
s.add_product('ORA', 12000)
s.dispose_capacity(s.get_total_inventory() - s.capacity)


#### Test ProcessingPlant
t = 1
p = processing_plants['P02']
p.add_product('ORA', 1600)
p.age()
p.add_product('ORA', 200)
p.dispose_capacity(p.get_total_inventory() - p.capacity)
assert p.inventory == [200, 1500, 0, 0]

new_process_list, cost_poj, cost_fcoj = p.manufacture(t)
while len(new_process_list) == 0:
    new_process_list, cost_poj, cost_fcoj = p.manufacture(t)
assert np.abs(cost_poj - 2000 * 1700 * (75.64766839 / 100)) < 1e-3
assert np.abs(cost_fcoj - 1000 * 1700 * (24.35233161 / 100)) < 1e-3
assert new_process_list[0].location == p
assert new_process_list[0].finish_time == 2
assert new_process_list[0].start_product == 'ORA'
assert new_process_list[0].end_product == 'POJ'
assert np.abs(new_process_list[0].amount - 1700 * (75.64766839 / 100)) < 1e-3
assert new_process_list[1].location == p
assert new_process_list[1].finish_time == 2
assert new_process_list[1].start_product == 'ORA'
assert new_process_list[1].end_product == 'FCOJ'
assert np.abs(new_process_list[1].amount - 1700 * (24.35233161  / 100)) < 1e-3