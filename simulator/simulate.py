from initialize import initialize
from utilities import *
import numpy as np
import pandas as pd
import sys

# input_file = sys.argv[1]

# Hard-code the file to use.  Note that we can use both the
# results .xlsm and the original decisions spreadsheet, because
# the results .xlsm contains the decision sheets.
input_file = ('''/Users/edz/Documents/Princeton/Senior/ORF411'''
              '''/OJ/not_grapefruit/Results/notgrapefruit2016.xlsm''')

storages, processing_plants, groves, markets, decisions = initialize(input_file)

processes = []
deliveries = []

sales = [{'ORA': 0, 'POJ': 0, 'ROJ': 0, 'FCOJ': 0}] * 48
cost = [{
    'purchase': {'raw': 0, 'futures': {'ORA': 0, 'FCOJ': 0}},
    'manufacturing': {'POJ': 0, 'FCOJ': 0, 'ROJ (reconstitution)': 0},
    'transportation': {'from_grove': 0, 'from_plants': 0, 'from_storages': 0},
    'inventory_hold': 0,
    'maintenance': {'storage': 0, 'processing': 0, 'tanker': 0},
    'capacity': {'storage': 0, 'processing': 0, 'tanker': 0}
}] * 48


# Starts at beginning of week 0
for t in xrange(0, 49):
    # Age all storages and processing plants.
    for storage in storages:
        storage.age()
    for processing_plant in processing_plants:
        processing_plant.age()

    # Check Processes that finished and create resulting Deliveries
    # (manufacturing, need to group by plant in order to send out tanker cars
    # / carriers), or adjust inventory (reconstitution).
    for process in processes:
        if process.finish_time == t:
            # Manufacturing
            if start_product == 'ORA':
                process.location.inventory['ORA'] -= process.amount
                # Send out Deliveries -- this will be weird with tanker cars...
            # Reconstitution
            elif start_product == 'FCOJ':
                process.location.inventory['XOJ'] -= process.amount
                process.location.inventory['ROJ'] += process.amount
            else:
                raise ValueError('Process must start with ORA or FCOJ')

    # Check Deliveries that arrive.  Add in all incoming deliveries, and then
    # do a capacity check afterwards (both storages and plants).
    for delivery in deliveries:
        if delivery.arrival_time == t:
            delivery.receiver.inventory[delivery.product] += delivery.amount
    for storage in storages:
        total_inventory = sum(
            [sum(vals) for vals in storage.inventory.values()])
        storage.dispose_capacity(total_inventory - storage.capacity)
    for processing_plant in processing_plants:
        total_inventory = sum(
            [sum(vals) for vals in processing_plant.inventory.values()])
        processing_plant.dispose_capacity(
            total_inventory - processing_plant.capacity)

    # Go through Groves and make spot purchases (create Deliveries).
    # Also make Futures deliveries for FLA.
    for grove in groves:
        new_deliveries, raw_cost, shipping_cost = grove.spot_purchase(t)
        deliveries += new_deliveries
        cost['purchase']['raw'] += raw_cost
        cost['transportation']['from_grove'] += shipping_cost

    # Go through Plants and manufacture (create Processes).
    for processing_plant in processing_plants:
        

    # Go through Storages and reconstitute (create Processes), don't forget
    # XOJ.

    # Go through Storages / Markets and sell

    # Calculate holding costs.






    # Check all deliveries for arrival / finish
    for delivery in deliveries:
        if delivery.arrival_time == t:
            delivery.receiver.inventory += 

        # When we increment inventories, that's when we need to
        # check for capacity disposal.
        pass

    # Grove: new spot purchases and shipping
    for grove in groves:

        # Realize a price.
        price = grove.realize_month_price()

        # Determine quantity to ask for based on multipliers from decisions,
        # and the realized price.
        quantity_df = decisions['spot_purchases']['quantities']
        multiplier_df = decisions['spot_purchases']['multipliers']
        quantity = apply_multipliers(grove.name, t, price, quantity_df,
                                     multiplier_df)

        # Execute the purchase (add new deliveries).
        deliveries += grove.spot_purchase(
            quantity, decisions['shipping']['from_grove'].loc[grove.name, :],
            t)

    # ProcessingPlant: new manufacturing processes
    for plant in processing_plants:
        poj_percentage = decisions['manufacturing'][plant.name]['POJ']
        deliveries += plant.process(poj_percentage, t)

    # Storage: new reconstitution processes
    for storage in storages:
        recon_percentage = decisions['reconstitution'].loc[storage.name][int(
            t / 4)]
        deliveries += storage.reconstitute(recon_percentage)
        storage.check_rotten()

    # Market: sell
    # Need to loop through storages in order to be able to do proportional
    # satisfying

    # Holding cost