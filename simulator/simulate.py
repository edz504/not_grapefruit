from initialize import initialize
from utilities import Delivery, Grove, Storage, ProcessingPlant, Market
import numpy as np
import pandas as pd
import sys

# input_file = sys.argv[1]

# Hard-code the file to use.  Note that we can use both the
# results .xlsm and the original decisions spreadsheet, because
# the results .xlsm contains the decision sheets.
input_file = ('''/Users/edz/Documents/Princeton/Senior/ORF411'''
              '''/OJ/not_grapefruit/Results/notgrapefruit2016.xlsm''')


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
