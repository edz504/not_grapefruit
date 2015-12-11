import numpy as np
import pandas as pd
import os
import sys
from utilities import *
from xlwings import Workbook, Range

def initialize(input_file):
    # Initialize the markets
    markets = {}
    ROOT_DIR = os.path.dirname(os.getcwd())
    wb = Workbook(
        os.path.join(ROOT_DIR,'reference/StaticData-mod.xlsx'))
    market_names = Range(
        'S->M', 'A2:B101', atleast_2d=True).value
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

        # TODO (Eddie): read in real demand coefficient beliefs later
        coefs = [(1000, -20), (1000, -20), (1000, -20), (1000, -20)]
        # TODO (Eddie): read in real demand variance beliefs later
        stats = [10, 10, 10, 10]
        markets[name] = Market(name=name,
                               region=region,
                               prices=prices,
                               demand_function_coefs=coefs,
                               demand_stats=stats)

    # To find the closest storage for each market, we need to retrieve the
    # distance matrix from the static data file, and then initialize the
    # storages.
    D = pd.DataFrame(np.array(
        Range('S->M', 'C2:BU101', atleast_2d=True).value))
    D.columns = Range('S->M', 'C1:BU1').value
    D.index = Range('S->M', 'B2:B101').value

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
        storages[name] = Storage(
            name=name,
            capacity=capacity,
            reconstitution_percentages=reconstitution_percentages,
            inventory={'ORA': [0] * 4,
                       'POJ': [0] * 8,
                       'ROJ': [0] * 12,
                       'FCOJ': [0] * 48,
                       'XOJ': [0] * 1
            }) # TODO (Eddie): Initialize inventory to leftover.

    # Each key is a storage name, the value is a list of the markets that it
    # will sell to.
    storage_closest_markets = dict(
        zip(all_storage_names,[[] for i in xrange(0, len(all_storage_names))]))

    # Filter out D to only be columns where we have storages open.
    D_open = D[storages.keys()]
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
        shipping_plan = {'POJ': dict(zip(storage_names,
                                         Range('shipping_manufacturing',
                                               (27, 4 + 2 * i),
                                               (26 + len(storages), 4 + 2 * i)).value)),
                         'FCOJ': dict(zip(storage_names,
                                         Range('shipping_manufacturing',
                                               (27, 5 + 2 * i),
                                               (26 + len(storages), 5 + 2 * i)).value))
                         }
        processing_plants[name] = ProcessingPlant(
            name=name,
            capacity=capacity,
            poj_proportion=poj_proportion,
            inventory={'ORA': [0] * 4,
                       'POJ': [0] * 8,
                       'ROJ': [0] * 12,
                       'FCOJ': [0] * 48,
            },
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
        shipping_plan = dict(zip(location_names,
                                 Range('shipping_manufacturing',
                                       'C{0}:J{0}'.format(6 + i)).value))
        # TODO (Eddie): Read in these stats from belief.
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