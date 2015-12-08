# from utilities import Delivery, Grove, Storage, ProcessingPlant, Market

#####
# Dummy definitions while teammates finish utilities:
class Storage(object):
    def __init__(self, name, capacity, inventory):
        self.name = name
        self.capacity = capacity
        self.inventory = inventory
class ProcessingPlant(object):
    def __init__(self, name, capacity, raw_inventory, manufactured_inventory,
                 tanker_cars):
        self.name = name
        self.capacity = capacity
        self.raw_inventory = raw_inventory
        self.manufactured_inventory = manufactured_inventory
        self.tanker_cars = tanker_cars
class Grove(object):
    def __init__(self, name, month):
        self.name = name
        self.month = month
######


import numpy as np
import pandas as pd
import sys
from xlwings import Workbook, Range

def initialize(input_file):
    wb = Workbook(input_file)
    # Initialize decisions dictionary
    decisions = {}

    # Initialize Storage Systems
    all_storage_names = Range('facilities', 'B36:B106').value
    num_storages = int(Range('basic_info', 'D8').value)
    storages = [None] * num_storages
    storage_capacities = Range('facilities', 'D36:D106').value
    for i in xrange(0, num_storages):
        name = Range('basic_info', 'E{0}'.format(10 + i)).value
        index = all_storage_names.index(name)
        capacity = storage_capacities[index]
        storages[i] = Storage(
            name=name,
            capacity=capacity,
            inventory=[(0, 0, 0, 0)] * 48)

    # Initialize Processing Plants
    all_processing_plant_names = Range('facilities', 'B6:B15').value
    num_processing_plants = int(Range('basic_info', 'B8').value)
    processing_plants = [None] * num_processing_plants
    processing_capacities = Range('facilities', 'D6:D15').value
    tanker_car_counts = Range('facilities', 'D21:D30').value
    for i in xrange(0, num_processing_plants):
        name = Range('basic_info', 'C{0}'.format(10 + i)).value
        index = all_processing_plant_names.index(name)
        capacity = processing_capacities[index]
        tanker_car_count = int(tanker_car_counts[index])
        processing_plants[i] = ProcessingPlant(
            name=name,
            capacity=capacity,
            raw_inventory=0,
            manufactured_inventory=[(0, 0, 0, 0)] * 48,
            tanker_cars=(tanker_car_count, 0, 0))
    # Initialize Groves
    groves = [Grove(name=grove, month=0)
              for grove in Range('raw_materials', 'B6:B11').value]

    # Capacity decisions
    decisions['capacity'] = {'processing': Range('facilities', 'C6:C15').value,
                             'tankers': Range('facilities', 'C21:C30').value,
                             'storage': Range('facilities', 'C36:C106').value}

    # Spot purchase decisions (quantities and multipliers)
    quantities_df = pd.DataFrame(Range('raw_materials',
                                       'C6:N11', atleast_2d=True).value,
                                 index=Range('raw_materials', 'B6:B11').value,
                                 columns=Range('raw_materials', 'C5:N5').value)
    multipliers_df = pd.DataFrame(Range('raw_materials',
                                        'C17:H22', atleast_2d=True).value,
                                  index=Range('raw_materials', 'B17:B22').value,
                                  columns=Range('raw_materials', 'C16:H16').value)
    decisions['spot_purchases'] = {
        'quantities': quantities_df,
        'multipliers': multipliers_df
    }


    # Futures decisions for this year aren't what we pick.  We're
    # really grabbing the decisions we made earlier.
    futures_maturing_this_year = Range('raw_materials', 'D36:M36').value
    total_price = (futures_maturing_this_year[0] * futures_maturing_this_year[1] +
                   futures_maturing_this_year[2] * futures_maturing_this_year[3] +
                   futures_maturing_this_year[4] * futures_maturing_this_year[5] +
                   futures_maturing_this_year[6] * futures_maturing_this_year[7] +
                   futures_maturing_this_year[8] * futures_maturing_this_year[9])

    arrival_df = pd.DataFrame(Range('raw_materials', 'C47:N48',
                                     atleast_2d=True).value,
                              index=Range('raw_materials', 'B47:B48').value,
                              columns=Range('raw_materials', 'C46:N46').value)

    decisions['futures'] = {'quantity': Range('raw_materials', 'P36').value,
                            'total_price': total_price * 2000, # lbs to tons
                            'arrivals': arrival_df
    }

    # Shipping and manufacturing decisions
    from_grove_df = pd.DataFrame(
        Range('shipping_and_manufacturing', (6, 3),
              (11, 2 + num_storages + num_processing_plants)).value,
              index=Range('shipping_and_manufacturing', 'B6:B11').value,
              columns=Range('shipping_and_manufacturing', 'C5:J5').value)
    decisions['shipping'] = {
        'from_grove': from_grove_df
    }

    manufacturing_df = pd.DataFrame(
        Range('shipping_and_manufacturing', (17, 3),
              (19, 2 + num_processing_plants * 2)).value)
    names = [name for name in
                [n for n in manufacturing_df.iloc[0, :] if n is not None]
             for i in xrange(0, 2)]
    manufacturing_df.columns = pd.MultiIndex.from_tuples(
        zip(names, manufacturing_df.iloc[1, :]))
    decisions['manufacturing'] = manufacturing_df.reindex(
        manufacturing_df.index.drop([0, 1]))

    decisions['shipping']['futures'] = dict(
        zip(Range('shipping_and_manufacturing', 'B27:B30').value,
            Range('shipping_and_manufacturing', 'C27:C30').value))

    from_plant_df = pd.DataFrame(
        Range('shipping_and_manufacturing', (25, 4),
              (30, 3 + num_processing_plants * 2)).value)
    names = [name for name in 
                [n for n in from_plant_df.iloc[0, :] if n is not None]
             for i in xrange(0, 2)]
    from_plant_df.columns = pd.MultiIndex.from_tuples(
        zip(names, from_plant_df.iloc[1, :]))
    decisions['shipping']['from_plant'] = from_plant_df.reindex(
        from_plant_df.index.drop([0, 1]))

    decisions['reconstitution'] = pd.DataFrame(
        Range('shipping_and_manufacturing',
              'C38:N41', atleast_2d=True).value,
        index=Range('shipping_and_manufacturing', 'B38:B41').value,
        columns = Range('shipping_and_manufacturing', 'C37:N37').value)

    # Pricing decisions
    months = Range('pricing', 'D5:O5').value
    regions = Range('pricing', 'C6:C12').value
    ora_df = pd.DataFrame(
        Range('pricing', 'D6:O12', atleast_2d=True).value,
        index=regions,
        columns=months)
    poj_df = pd.DataFrame(
        Range('pricing', 'D15:O21', atleast_2d=True).value,
        index=regions,
        columns=months)
    roj_df = pd.DataFrame(
        Range('pricing', 'D24:O30', atleast_2d=True).value,
        index=regions,
        columns=months)
    fcoj_df = pd.DataFrame(
        Range('pricing', 'D33:O39', atleast_2d=True).value,
        index=regions,
        columns=months)
    decisions['pricing'] = {
        'ORA': ora_df,
        'POJ': poj_df,
        'ROJ': roj_df,
        'FCOJ': fcoj_df
    }
    
    return decisions


# decisions, groves, storages, processing_plants = initialize(input_file)
# deliveries = []

# sales = [None] * 48
# cost = [None] * 48

# for t in xrange(0, 49):
#     # Check all deliveries for arrival / finish

#     # Grove: new spot purchases and shipping

#     # ProcessingPlant: new manufacturing processes and shipping

#     # Storage: new reconstitution

#     # Market: sell
