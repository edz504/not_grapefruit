import numpy as np
import pandas as pd
import os
import sys
from utilities import *
from xlwings import Workbook, Range

def initialize_inventory(input_file):
    wb = Workbook(input_file)
    inv = {}
    num_storages = int(Range('basic_info', 'D8').value)
    for i in xrange(0, num_storages):
        name = Range('basic_info', 'E{0}'.format(10 + i)).value
        # Inventory before sales
        this_inv = {
            'ORA': Range(name, 'AY95:AY98').value,
            'POJ': Range(name, 'AY100:AY107').value,
            'ROJ': Range(name, 'AY109:AY120').value,
            'FCOJ': Range(name, 'AY122:AY169').value
        }
        these_sales = {
            'ORA': Range(name, 'AY176').value,
            'POJ': Range(name, 'AY178').value,
            'ROJ': Range(name, 'AY180').value,
            'FCOJ': Range(name, 'AY182').value
        }
        for product, sales in these_sales.iteritems():
            amount_to_remove = sales
            i = len(this_inv[product]) - 1
            # Subtract inventory using sales, priority = age
            while amount_to_remove > 0 and i >= 0:
                inventory_this_age = this_inv[product][i]
                if inventory_this_age > amount_to_remove:
                    this_inv[product][i] -= amount_to_remove
                else:
                    this_inv[product][i]= 0

                amount_to_remove -= inventory_this_age
                i -= 1

        this_inv['XOJ'] = [0]
        inv[name] = this_inv

    return inv

def initialize(input_file, initial_inventory):
    # Initialize the markets
    markets = {}
    ROOT_DIR = os.path.dirname(os.getcwd())
    wb = Workbook(
        os.path.join(ROOT_DIR,'reference/StaticData-mod.xlsx'))
    market_names = Range(
        'S->M', 'A2:B101', atleast_2d=True).value
    demand_coef_df = pd.read_csv(
        os.path.join(ROOT_DIR,
                     'demand_pipeline/demand_fit_coefs.csv'))
    wb = Workbook(input_file)
    for val in market_names:
        name = val[1]
        region = val[0]
        prices = {
            'ORA': Range('pricing', 'D{0}:O{0}'.format(
                6 + REGIONS.index(region))).value,
            'POJ': Range('pricing', 'D{0}:O{0}'.format(
                15 + REGIONS.index(region))).value,
            'ROJ': Range('pricing', 'D{0}:O{0}'.format(
                24 + REGIONS.index(region))).value,
            'FCOJ': Range('pricing', 'D{0}:O{0}'.format(
                33 + REGIONS.index(region))).value
        }

        region_demands = demand_coef_df[demand_coef_df['region'] == region]
        coefs = dict(zip(region_demands['product'],
                     zip(region_demands['a'],
                         region_demands['b'])))
        markets[name] = Market(name=name,
                               region=region,
                               prices=prices,
                               demand_function_coefs=coefs)

    # To find the closest storage for each market, we need to retrieve the
    # distance matrix from the static data file, and then initialize the
    # storages.
    wb = Workbook(
        os.path.join(ROOT_DIR,'reference/StaticData-mod.xlsx'))
    D_sm = pd.DataFrame(np.array(
        Range('S->M', 'C2:BU101', atleast_2d=True).value),
                        columns=Range('S->M', 'C1:BU1').value,
                        index=Range('S->M', 'B2:B101').value)
    # Also retrieve the other D matrices for Grove and ProcessingPlant shipping
    # plan values, while we have this workbook open.
    D_ps = pd.DataFrame(np.array(
        Range('P->S', 'B2:K72', atleast_2d=True).value),
                        columns=Range('P->S', 'B1:K1').value,
                        index=Range('P->S', 'A2:A72').value)
    D_gps = pd.DataFrame(np.array(
        Range('G->PS', 'B2:E82', atleast_2d=True).value),
                         columns=Range('G->PS', 'B1:E1').value,
                         index=Range('G->PS', 'A2:A82').value)

    wb = Workbook(input_file)
    # Initialize Storage Systems
    all_storage_names = Range('facilities', 'B36:B106').value
    num_storages = int(Range('basic_info', 'D8').value)
    storages = {}
    storage_capacities = Range('facilities', 'D36:D106').value
    for i in xrange(0, num_storages):
        name = Range('basic_info', 'E{0}'.format(10 + i)).value
        index = all_storage_names.index(name)
        capacity = storage_capacities[index]
        reconstitution_percentages = Range(
            'shipping_manufacturing', 'C{0}:N{0}'.format(38 + i)).value
        if name in initial_inventory.keys():
            inv = initial_inventory[name]
        else:
            inv = {
                'XOJ': [0],
                'ORA': [0] * 4,
                'POJ': [0] * 8,
                'ROJ': [0] * 12,
                'FCOJ': [0] * 48
            }
        storages[name] = Storage(
            name=name,
            capacity=capacity,
            reconstitution_percentages=reconstitution_percentages,
            inventory=inv)

    # Each key is a storage name, the value is a list of the markets that it
    # will sell to.
    storage_closest_markets = dict(
        zip(all_storage_names,[[] for i in xrange(0, len(all_storage_names))]))

    # Filter out D_sm to only be columns where we have storages open.
    D_open = D_sm[storages.keys()]
    for market_name, market in markets.iteritems():
        dists = D_open.loc[market_name, :]
        min_dist = min(dists)
        min_ind = list(dists).index(min_dist)
        storage_closest_markets[D_open.columns[min_ind]].append((market,
                                                                 min_dist))

    for name, storage in storages.iteritems():
        storage.markets = storage_closest_markets[name]

    # Initialize Processing Plants
    all_processing_plant_names = Range('facilities', 'B6:B15').value
    num_processing_plants = int(Range('basic_info', 'B8').value)
    processing_plants = {}
    processing_capacities = Range('facilities', 'D6:D15').value
    tanker_car_counts = Range('facilities', 'D21:D30').value
    storage_names = Range('shipping_manufacturing', 'B27:B{0}'.format(
        26 + len(storages))).value
    for i in xrange(0, num_processing_plants):
        name = Range('basic_info', 'C{0}'.format(10 + i)).value
        index = all_processing_plant_names.index(name)
        capacity = processing_capacities[index]
        poj_proportion = Range('shipping_manufacturing', (19, 3 + 2 * i)).value
        tanker_car_count = int(tanker_car_counts[index])
        dists = D_ps.loc[storage_names, name]
        shipping_plan = {'POJ': dict(zip(storage_names,
                                         zip(Range('shipping_manufacturing',
                                                   (27, 4 + 2 * i),
                                                   (26 + len(storages), 4 + 2 * i)).value,
                                             dists))),
                         'FCOJ': dict(zip(storage_names,
                                         zip(Range('shipping_manufacturing',
                                                   (27, 5 + 2 * i),
                                                   (26 + len(storages), 5 + 2 * i)).value,
                                             dists)))
                         }
        processing_plants[name] = ProcessingPlant(
            name=name,
            capacity=capacity,
            poj_proportion=poj_proportion,
            inventory=[0] * 4,
            tanker_cars={'at_home': tanker_car_count,
                         'going_out': 0,
                         'coming_home': 0},
            shipping_plan=shipping_plan)
    
    # Initialize Groves (store spot purchase and from_grove shipping decisions
    # in these objects)
    groves = {}
    location_names = Range('shipping_manufacturing', 'C5:J5').value

    raw_price_beliefs_mean = pd.read_csv(os.path.join(ROOT_DIR, 
        'grove_beliefs/raw_price_beliefs_mean.csv'))
    raw_price_beliefs_std = pd.read_csv(os.path.join(ROOT_DIR, 
        'grove_beliefs/raw_price_beliefs_std.csv'))
    exchange_rate_beliefs_mean = pd.read_csv(os.path.join(ROOT_DIR, 
        'grove_beliefs/exchange_rate_beliefs_mean.csv'))
    exchange_rate_beliefs_std = pd.read_csv(os.path.join(ROOT_DIR, 
        'grove_beliefs/exchange_rate_beliefs_std.csv'))
    quantity_beliefs_mean = pd.read_csv(os.path.join(ROOT_DIR, 
        'grove_beliefs/quantity_beliefs_mean.csv'))
    quantity_beliefs_std = pd.read_csv(os.path.join(ROOT_DIR, 
        'grove_beliefs/quantity_beliefs_std.csv'))

    for i, grove_name in enumerate(Range('raw_materials', 'B6:B11').value):
        desired_quantities = Range('raw_materials',
                                   'C{0}:N{0}'.format(6 + i)).value
        multipliers = Range('raw_materials',
                            'C{0}:H{0}'.format(17 + i)).value
        name_adj = 'FLA'
        if grove_name not in ['BRA', 'SPA']:
            name_adj = grove_name
        dists = D_gps.loc[location_names, name_adj]
        shipping_plan = dict(zip(location_names,
                                 zip(Range('shipping_manufacturing',
                                       'C{0}:J{0}'.format(6 + i)).value,
                                     dists)))

        price_stats = [None] * 12
        exchange_stats = [None] * 12
        harvest_stats = [None] * 12
        for j, month in enumerate(MONTHS):
            price_stats[j] = (
                float(raw_price_beliefs_mean.loc[
                    (raw_price_beliefs_mean['month'] == month) &
                    (raw_price_beliefs_mean['grove'] == grove_name)]['price']),
                float(raw_price_beliefs_std.loc[
                    (raw_price_beliefs_std['month'] == month) &
                    (raw_price_beliefs_std['grove'] == grove_name)]['price']))
            if grove_name in ['BRA', 'SPA']:
                if grove_name == 'BRA':
                    foreign = 'BRA Real'
                else:
                    foreign = 'SPA Euro'
                exchange_stats[j] = (
                    float(exchange_rate_beliefs_mean.loc[
                        (exchange_rate_beliefs_mean['month'] == month) &
                        (exchange_rate_beliefs_mean['foreign'] == foreign)]['rate']),
                    float(exchange_rate_beliefs_std.loc[
                        (exchange_rate_beliefs_std['month'] == month) &
                        (exchange_rate_beliefs_std['foreign'] == foreign)]['rate']))
            else:
                exchange_stats[j] = (None, None)
            harvest_stats[j] = (
                float(quantity_beliefs_mean.loc[
                    (quantity_beliefs_mean['month'] == month) &
                    (quantity_beliefs_mean['grove'] == grove_name)]['quantity']),
                float(quantity_beliefs_std.loc[
                    (quantity_beliefs_std['month'] == month) &
                    (quantity_beliefs_std['grove'] == grove_name)]['quantity']))
        groves[grove_name] = Grove(name=grove_name,
                                   price_stats=price_stats,
                                   exchange_stats=exchange_stats,
                                   harvest_stats=harvest_stats,
                                   desired_quantities=desired_quantities,
                                   multipliers=multipliers,
                                   shipping_plan=shipping_plan)

    # Initialize decisions dictionary -- this will contain capacity and futures
    # decisions, which do not conceptualize easily with the objects.
    decisions = {}

    # Capacity decisions
    old_plant = Range('facilities', 'D6:D15').value
    new_plant = Range('facilities', 'G6:G15').value
    old_tankers = Range('facilities', 'D21:D30').value
    new_tankers = Range('facilities', 'G21:G30').value
    old_storage = Range('facilities', 'D36:D106').value
    new_storage = Range('facilities', 'G36:G106').value
    decisions['capacity'] = {'processing': dict(zip(all_processing_plant_names,
                                                    zip(old_plant, new_plant))),
                             'tankers': dict(zip(all_processing_plant_names,
                                                 zip(old_tankers, new_tankers))),
                             'storage': dict(zip(all_storage_names,
                                             zip(old_storage, new_storage)))
    }

    # Futures decisions for this year aren't what we pick.  We're
    # really grabbing the decisions we made earlier.
    # Get FCOJ first.
    futures_maturing_this_year = Range('raw_materials', 'D36:M36').value
    total_price = (futures_maturing_this_year[0] * futures_maturing_this_year[1] +
                   futures_maturing_this_year[2] * futures_maturing_this_year[3] +
                   futures_maturing_this_year[4] * futures_maturing_this_year[5] +
                   futures_maturing_this_year[6] * futures_maturing_this_year[7] +
                   futures_maturing_this_year[8] * futures_maturing_this_year[9])

    arrivals = Range('raw_materials', 'C48:N48').value

    decisions['futures'] = {
        'FCOJ': {'quantity': Range('raw_materials', 'P36').value,
                 'total_price': total_price * 2000, # lbs to tons
                 'arrivals': arrivals,
                 'shipping': dict(zip(Range('shipping_manufacturing',
                                          'B27:B30').value,
                                      Range('shipping_manufacturing',
                                          'C27:C30').value))
                 }
    }

    # Now get the ORA futures (we probably will never buy these).
    futures_maturing_this_year = Range('raw_materials', 'D30:M30').value
    total_price = (futures_maturing_this_year[0] * futures_maturing_this_year[1] +
                   futures_maturing_this_year[2] * futures_maturing_this_year[3] +
                   futures_maturing_this_year[4] * futures_maturing_this_year[5] +
                   futures_maturing_this_year[6] * futures_maturing_this_year[7] +
                   futures_maturing_this_year[8] * futures_maturing_this_year[9])

    arrivals = Range('raw_materials', 'C47:N47').value
    decisions['futures']['ORA'] = {
        'quantity': Range('raw_materials', 'P30').value,
        'total_price': total_price * 2000,
        'arrivals': arrivals
    } # Note no shipping like for FCOJ -- it's stored in the FLA Grove object.

    return storages, processing_plants, groves, markets, decisions