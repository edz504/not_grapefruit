from initialize import initialize
from utilities import *
import numpy as np
import pandas as pd
import sys
import time

# input_file = sys.argv[1]

# Hard-code the file to use.  Note that we can use both the
# results .xlsm and the original decisions spreadsheet, because
# the results .xlsm contains the decision sheets.
input_file = ('''/Users/edz/Documents/Princeton/Senior/ORF411'''
              '''/OJ/not_grapefruit/Results/notgrapefruit2016.xlsm''')

print 'Initializing...'
start = time.time()
storages, processing_plants, groves, markets, decisions = initialize(input_file)
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


processes = []
deliveries = []


# Starts at beginning of week 0
for t in xrange(0, 49):
    month_ind = int(t / 4)

    # Age all storages and processing plants.
    for storage in storages.values():
        storage.age()
    for processing_plant in processing_plants.values():
        processing_plant.age()

    # Check Processes that finished and create resulting Deliveries
    # (manufacturing, need to group by plant in order to send out tanker cars
    # / carriers), or adjust inventory (reconstitution).
    for process in processes:
        if process.finish_time == t:
            # Manufacturing
            if start_product == 'ORA':
                process.location.remove_product('ORA', process.amount)
                # TODO (Eddie):
                # Send out Deliveries -- this will be weird with tanker cars...
                # Make sure to add to from_plant costs, and tanker hold cost.
            # Reconstitution
            elif start_product == 'FCOJ':
                process.location.remove_product('XOJ', process.amount)
                process.location.add_product('ROJ', process.amount)
            else:
                raise ValueError('Process must start with ORA or FCOJ')

    # Check Deliveries that arrive.  Add in all incoming deliveries, and then
    # do a capacity check afterwards (both storages and plants).
    for delivery in deliveries:
        if delivery.arrival_time == t:
            delivery.receiver.add_product(delivery.product, delivery.amount)
    for storage in storages.values():
        storage.dispose_capacity(
            storage.get_total_inventory() - storage.capacity)
    for processing_plant in processing_plants.values():
        processing_plant.dispose_capacity(
            processing_plant.get_total_inventory() - processing_plant.capacity)

    # Go through Groves and make spot purchases (create Deliveries).
    # Also make Futures deliveries for FLA.
    for grove in groves.values():
        new_deliveries, raw_cost, shipping_cost = grove.spot_purchase(t)
        deliveries += new_deliveries
        cost['purchase']['raw'] += raw_cost
        cost['transportation']['from_grove'] += shipping_cost

        if grove.name == 'FLA':
            # ORA futures
            ORA = decisions['futures']['ORA']
            total_weekly_quantity = (ORA['quantity'] *
                (ORA['arrivals'][month_ind] / 100) * 0.25)
            for location, proportion in grove.shipping_plan.iteritems():
                if location[0] == 'P':
                    receiver = processing_plants[location]
                else:
                    receiver = storages[location]
                deliveries.append(
                    Delivery(sender=grove,
                             receiver=receiver,
                             arrival_time=(t+1),
                             amount=total_weekly_quantity * proportion))

            # FCOJ futures
            FCOJ = decisions['futures']['FCOJ']
            total_weekly_quantity = (FCOJ['quantity'] *
                (FCOJ['arrivals'][month_ind] / 100) * 0.25)
            for storage_name, proportion in FCOJ['shipping'].iteritems():
                receiver = storages[storage_name]
                deliveries.append(
                    Delivery(sender=grove,
                             receiver=receiver,
                             arrival_time=(t + 1),
                             amount=total_weekly_quantity * proportion))

    # Go through Plants and manufacture (create Processes).
    for processing_plant in processing_plants.values():
        new_processes, cost_poj, cost_fcoj = processing_plant.manufacture(t)
        processes += new_processes
        cost['manufacturing']['POJ'] += cost_poj
        cost['manufacturing']['FCOJ'] += cost_fcoj

    # Go through Storages and reconstitute (create Processes), using the XOJ.
    for storage in storages.values():
        recon_percent = storage.reconstitution_percentages[month_ind]
        Y = recon_percent * storage.inventory['FCOJ']
        storage.remove_product('FCOJ', Y)
        storage.add_product('XOJ', Y)
        new_processes, cost = storage.reconstitute(t)
        processes.append(new_processes)
        cost['manufacturing']['ROJ (reconstitution)'] += cost

    # Go through Storages and sell to each of its markets.
    for storage in storages.values():
        for product in PRODUCTS:
            market_demands = [None] * len(storage.markets)
            market_dists = [None] * len(storage.markets)
            for i, market_tuple in enumerate(storage.markets):
                market = market_tuple[0]
                market_dists[i] = market_tuple[1]
                market_demands[i] = market.realize_demand(product, t)
            market_sell = [None] * len(storage.markets)
            inv = storage.get_total_inventory(product)
            total_demand = sum(market_demands)
            # If demand exceeds inventory, sell to the markets proportionally.
            if total_demand <= inv:
                market_sell = market_demands
                storage.remove_product(product, total_demand)
                sales[product] += total_demand
            else:
                market_demands_proportions = [d / total_demand
                                              for d in market_demands]
                market_sell = [inv * p
                               for p in market_demands_proportions]
                storage.remove_product(product, inv)
                sales[product] += inv
            for i, sale in enumerate(market_sell):
                price = market.prices[product][month_ind]
                revenue[product] += price * sale
                cost['transportation']['from_storages'] += (1.2 *
                                                            market_dists[i] *
                                                            sale)

    # Calculate holding costs.
    for storage in storages.values():
        cost['inventory_hold'] += storage.get_total_inventory() * 60

# Add in annual costs
cost['purchase']['futures']['ORA'] += decisions['futures']['ORA']['total_price']
cost['purchase']['futures']['FCOJ'] += decisions['futures']['FCOJ']['total_price']
cost['maintenance']['storage'] += sum([7.5e6 + 650 * s.capacity
                                       for s in storages.values()])
cost['maintenance']['processing'] += sum([8.0e6 + 2500 * p.capacity
                                          for p in processing_plants.values()])

for storage, (old, new) in decisions['capacity']['storage'].iteritems():
    # Buying capacity (but not a new storage)
    if old != 0 and new > old:
        this_cost = 6000 * (new - old)

    # Selling capacity (but not an entire storage)
    elif old > new:
        this_cost = .8 * 6000 * (new - old)

    # Selling an entire storage
    elif old > new and new == 0:
        this_cost = .8 * (9.0e6 + 6000 * (new - old))

    # Buying an entire new storage
    elif old == 0 and new > old:
        this_cost = 9.0e6 + 6000 * (new - old)

    # Make sure this is the only other case
    elif old == 0 == new:
        this_cost = 0

    cost['capacity_change']['storage'] += this_cost

for plant, (old, new) in decisions['capacity']['processing'].iteritems():
    # Buying capacity (but not a new plant)
    if old != 0 and new > old:
        this_cost = 8000 * (new - old)

    # Selling capacity (but not an entire plant)
    elif old > new:
        this_cost = .7 * 8000 * (new - old)

    # Selling an entire plant
    elif old > new and new == 0:
        this_cost = .7 * (12.0e6 + 8000 * (new - old))

    # Buying an entire new plant
    elif old == 0 and new > old:
        this_cost = 12.0e6 + 8000 * (new - old)

    # Make sure this is the only other case
    elif old == 0 == new:
        this_cost = 0

    print this_cost
    cost['capacity_change']['processing'] += this_cost

for plant, (old, new) in decisions['capacity']['tankers'].iteritems():
    if new > old:
        cost['capacity_change']['tanker'] += 100000 * (new - old)
    else:
        cost['capacity_change']['tanker'] -= .6 * 100000 * (old - new)