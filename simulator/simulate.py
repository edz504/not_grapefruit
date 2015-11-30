from utilities import Delivery, Grove, Storage, ProcessingPlant, Market
from xlwings import Workbook, Range

input_file = ('''/Users/edz/Documents/Princeton/Senior/ORF411'''
            '''/OJ/not_grapefruit/Results/notgrapefruit2015.xlsm''')
wb = Workbook(input_file)

groves = []
storages = []
processing_plants = []
deliveries = []

# Store decisions as dictionary
decisions = {}

sales = [None] * 48
cost = [None] * 48

for t in xrange(0, 49):
    # Check all deliveries for arrival / finish

    # Grove: new spot purchases and shipping

    # ProcessingPlant: new manufacturing processes and shipping

    # Storage: new reconstitution

    # Market: sell
