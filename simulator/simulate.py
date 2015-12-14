from initialize import *
from utilities import *
import copy
import math
import numpy as np
import pandas as pd
import sys
import time

# input_file = sys.argv[1]
# last_year_file = sys.argv[2]

# Hard-code the file to use.  Note that we can use both the
# results .xlsm and the original decisions spreadsheet, because
# the results .xlsm contains the decision sheets.
ROOT_DIR = os.path.dirname(os.getcwd())
input_file = os.path.join(ROOT_DIR,'decisions/notgrapefruit2018.xlsm')

# We also need the Results file of the previous year in order to
# initialize the inventory.
last_year_file = os.path.join(ROOT_DIR, 'results/notgrapefruit2017.xlsm')

print 'Initializing...'
start = time.time()
initial_inventory, scheduled_to_ship_in = initialize_inventory(
    last_year_file)
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

# Add ORA spot purchase deliveries to P, S, arrival week 1
# (current decision)
for grove in groves.values():
    new_deliveries, raw_cost, shipping_cost = grove.spot_purchase(
        0, storages, processing_plants, month_index=0)
    deliveries += new_deliveries
    cost['purchase']['raw'] += raw_cost
    cost['transportation']['from_grove'] += shipping_cost


    # Add futures deliveries to S, arrival week 1
    # (current decision)
    if grove.name == 'FLA':
        # ORA futures
        ORA = decisions['futures']['ORA']
        total_weekly_quantity = (ORA['quantity'] *
            (ORA['arrivals'][0] / 100) * 0.25)
        for location, proportion in grove.shipping_plan.iteritems():
            if proportion[0] is None or proportion[0] == 0:
                continue
            else:
                prop = proportion[0] / 100
            if location[0] == 'P':
                receiver = processing_plants[location]
            else:
                receiver = storages[location]
            deliveries.append(
                Delivery(sender=grove,
                         receiver=receiver,
                         arrival_time=1,
                         product='ORA',
                         amount=total_weekly_quantity * prop))

        # FCOJ futures
        FCOJ = decisions['futures']['FCOJ']
        total_weekly_quantity = (FCOJ['quantity'] *
            (FCOJ['arrivals'][0] / 100) * 0.25)
        for storage_name, proportion in FCOJ['shipping'].iteritems():
            receiver = storages[storage_name]
            if proportion == 0:
                continue
            else:
                prop = proportion / 100
            deliveries.append(
                Delivery(sender=grove,
                         receiver=receiver,
                         arrival_time=1,
                         product='FCOJ',
                         amount=total_weekly_quantity * prop))



# Starts at beginning of week 1
for t in xrange(1, 49):

    print 'Beginning week {0}'.format(t)
    month_ind = int((t - 1) / 4)

    # Age all storages and processing plants.
    for storage in storages.values():
        storage.age()
    for processing_plant in processing_plants.values():
        processing_plant.age()

    # Check tanker_car_fleets arriving
    tmp_tanker_car_fleets = [] # Keep new list because remove() doesn't work
    for fleet in tanker_car_fleets:
        if fleet.arrival_time == t:
            fleet.plant.tanker_cars['at_home'] += fleet.size
            fleet.plant.tanker_cars['going_out'] = 0
        else:
            tmp_tanker_car_fleets.append(fleet)
    tanker_car_fleets = tmp_tanker_car_fleets

    # Check Processes that finished and create resulting Deliveries
    # (manufacturing, need to group by plant in order to send out tanker cars
    # / carriers), or adjust inventory (reconstitution).
    total_product_by_plant = dict(zip(processing_plants.keys(),
                                      [0] * len(processing_plants)))
    processes_by_plant = dict(zip(processing_plants.keys(),
                                  [[]] * len(processing_plants)))
    tmp_processes = []
    for process in processes:
        if process.finish_time == t:
            # Manufacturing
            if process.start_product == 'ORA':
                process.location.remove_product('ORA', process.amount)
                # Aggregate the total processed product at each plant
                total_product_by_plant[process.location.name] += process.amount
                # Also keep a list of the processes that this plant has finishing
                prev_list = copy.copy(processes_by_plant[process.location.name])
                processes_by_plant[process.location.name] = prev_list + [process]

            # Reconstitution
            elif process.start_product == 'FCOJ':
                process.location.remove_product('XOJ', process.amount)
                process.location.add_product('ROJ', process.amount)
            else:
                raise ValueError('Process must start with ORA or FCOJ')
        else:
            tmp_processes.append(process)
    processes = tmp_processes

    # Go through each plant now that we know how much product it has finished
    # processing.
    for plant_name, total_product in total_product_by_plant.iteritems():
        if total_product == 0:
            continue
        plant = processing_plants[plant_name]
        tanker_cars_needed = math.ceil(total_product / 30.)
        if plant.tanker_cars['at_home'] > tanker_cars_needed:
            plant.tanker_cars['going_out'] = tanker_cars_needed
            plant.tanker_cars['at_home'] -= tanker_cars_needed

            # Add new TankerCarFleet that will come back in two time steps
            tanker_car_fleets.append(
                TankerCarFleet(plant, t + 2, tanker_cars_needed))

            # Add new Deliveries to Storages according to shipping plan
            total_dist = {}
            for process in processes_by_plant[plant_name]:
                # Go through all storages to ship to
                product_shipping_plan = plant.shipping_plan[process.end_product]
                for storage_name in product_shipping_plan:
                    proportion = product_shipping_plan[storage_name][0]
                    if proportion is not None and proportion != 0:
                        prop = proportion / 100                
                        deliveries.append(
                            Delivery(sender=plant,
                                     receiver=storages[storage_name],
                                     arrival_time = t + 1,
                                     product=process.end_product,
                                     amount=process.amount * prop))
                        if storage_name not in total_dist.keys():
                            total_dist[storage_name] = product_shipping_plan[storage_name][1]

            # Add to travel and holding cost.
            cost['transportation']['from_plants'] += (36 * sum(total_dist.values()) *
                                                      tanker_cars_needed)
            cost['maintenance']['tanker'] += 10 * plant.tanker_cars['at_home']
        else:
            # Deal with carriers
            raise ValueError('''Needed tanker cars is more than at_home,'''
                             '''and we don't use carriers.''')
            

    # Check Deliveries that arrive.  Add in all incoming deliveries, and then
    # do a capacity check afterwards (both storages and plants).
    tmp_deliveries = []
    for delivery in deliveries:
        if delivery.arrival_time == t:
            # print 'Delivery from {0} to {1} of {2} {3} arrived'.format(
            #     delivery.sender.name, delivery.receiver.name,
            #     delivery.amount, delivery.product)
            delivery.receiver.add_product(delivery.product, delivery.amount)
        else:
            tmp_deliveries.append(delivery)
    deliveries = tmp_deliveries
    for storage in storages.values():
        storage.dispose_capacity(
            storage.get_total_inventory() - storage.capacity)
    for processing_plant in processing_plants.values():
        processing_plant.dispose_capacity(
            processing_plant.get_total_inventory() - processing_plant.capacity)

    # Go through Groves and make spot purchases (create Deliveries).
    # Also make Futures deliveries for FLA.
    for grove in groves.values():
        new_deliveries, raw_cost, shipping_cost = grove.spot_purchase(t,
            storages, processing_plants)
        deliveries += new_deliveries
        cost['purchase']['raw'] += raw_cost
        cost['transportation']['from_grove'] += shipping_cost

        if grove.name == 'FLA':
            # ORA futures
            ORA = decisions['futures']['ORA']
            total_weekly_quantity = (ORA['quantity'] *
                (ORA['arrivals'][month_ind] / 100) * 0.25)
            for location, proportion in grove.shipping_plan.iteritems():
                if proportion[0] is None or proportion[0] == 0:
                    continue
                else:
                    prop = proportion[0] / 100
                if location[0] == 'P':
                    receiver = processing_plants[location]
                else:
                    receiver = storages[location]
                deliveries.append(
                    Delivery(sender=grove,
                             receiver=receiver,
                             arrival_time=(t + 1),
                             product='ORA',
                             amount=total_weekly_quantity * prop))

            # FCOJ futures
            FCOJ = decisions['futures']['FCOJ']
            total_weekly_quantity = (FCOJ['quantity'] *
                (FCOJ['arrivals'][month_ind] / 100) * 0.25)
            for storage_name, proportion in FCOJ['shipping'].iteritems():
                receiver = storages[storage_name]
                if proportion == 0:
                    continue
                else:
                    prop = proportion / 100
                deliveries.append(
                    Delivery(sender=grove,
                             receiver=receiver,
                             arrival_time=(t + 1),
                             product='FCOJ',
                             amount=total_weekly_quantity * prop))

    # Go through Plants and manufacture (create Processes).
    for processing_plant in processing_plants.values():
        new_processes, cost_poj, cost_fcoj = processing_plant.manufacture(t)
        processes += new_processes
        cost['manufacturing']['POJ'] += cost_poj
        cost['manufacturing']['FCOJ'] += cost_fcoj

    # Go through Storages and reconstitute (create Processes), using the XOJ.
    for storage in storages.values():
        new_processes, recon_cost = storage.reconstitute(t)
        processes += new_processes
        cost['manufacturing']['ROJ (reconstitution)'] += recon_cost

    print 'Storage inventories before selling:'
    # Go through Storages and sell to each of its markets.
    for storage in storages.values():
        print storage.inventory
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
            # print '{0}, {1}: inventory = {2}, demand = {3}'.format(
            #     storage.name, product, inv, total_demand)

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
                revenues[product] += price * sale * 2000
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

for storage_name, (old, new) in decisions['capacity']['storage'].iteritems():
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

for plant_name, (old, new) in decisions['capacity']['processing'].iteritems():
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

    cost['capacity_change']['processing'] += this_cost

for plant_name, (old, new) in decisions['capacity']['tankers'].iteritems():
    if new > old:
        cost['capacity_change']['tanker'] += 100000 * (new - old)
    else:
        cost['capacity_change']['tanker'] -= .6 * 100000 * (old - new)

total_revenue = sum(revenues.values())
print 'Total Revenue: {0}'.format(total_revenue)
total_cost = (cost['purchase']['raw'] + sum(cost['purchase']['futures'].values()) +
              sum(cost['transportation'].values()) +
              sum(cost['maintenance'].values()) +
              sum(cost['capacity_change'].values()) +
              cost['inventory_hold'] +
              sum(cost['manufacturing'].values()))
print 'Total Cost: {0}'.format(total_cost)
print 'Profit: {0}'.format(total_revenue - total_cost)