import sys
from utilities import Delivery, Grove, Storage, ProcessingPlant, Market
from xlwings import Workbook, Range

input_file = sys.argv[1]
# Hard-code the file to use.  Note that we can use both the
# results .xlsm and the original decisions spreadsheet, because
# the results .xlsm contains the decision sheets.
input_file = ('''/Users/edz/Documents/Princeton/Senior/ORF411'''
              '''/OJ/not_grapefruit/Results/notgrapefruit2016.xlsm''')

def initialize(input_file):
    wb = Workbook(input_file)

    # Initialize Storage Systems
    all_storage_names = Range('facilities', 'B36:B106').value
    num_storages = Range('basic_info', 'D8').value
    storages = [None] * num_storages
    storage_capacities = Range('facilities', 'D36:D106').value
    for i in xrange(0, num_storages):
        name = Range('basic_info', 'E{0}'.format(10 + i)).value
        index = all_processing_plant_names.index(name)
        capacity = storage_capacities[index]
        # May need to initialize with empty inventory
        storages[i] = Storage(
            name=name,
            capacity=capacity,
            inventory=[(0, 0, 0, 0)] * 48)

    # Initialize Processing Plants
    all_processing_plant_names = Range('facilities', 'B6:B15').value
    num_processing_plants = Range('basic_info', 'B8').value
    processing_plants = [None] * num_processing_plants
    processing_capacities = Range('facilities', 'D6:D15').value
    tanker_car_counts = Range('facilities', 'D21:D30').value
    for i in xrange(0, num_processing_plants):
        name = Range('basic_info', 'C{0}'.format(10 + i)).value
        index = all_processing_plant_names.index(name)
        capacity = processing_capacities[index]
        tanker_car_count = tanker_car_counts[index]
        processing_plants[i] = ProcessingPlant(
            name=name,
            capacity=capacity,
            raw_inventory=0,
            manufactured_inventory=[(0, 0, 0, 0)] * 48,
            tanker_cars=(tanker_car_count, 0, 0))

    return storages, processing_plants


decisions, groves, storages, processing_plants = initialize(input_file)
deliveries = []

sales = [None] * 48
cost = [None] * 48

for t in xrange(0, 49):
    # Check all deliveries for arrival / finish

    # Grove: new spot purchases and shipping

    # ProcessingPlant: new manufacturing processes and shipping

    # Storage: new reconstitution

    # Market: sell
