from xlwings import Workbook, Range
import numpy as np
import pandas as pd
import os

ROOT_DIR = os.path.dirname(os.getcwd())
months = ['Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar',
          'Apr', 'May', 'Jun', 'Jul', 'Aug']
regions = ['NE', 'MA', 'SE', 'MW', 'DS', 'NW', 'SW']

wb = Workbook(os.path.join(ROOT_DIR,
              'results/notgrapefruit2016.xlsm'))

# ORA is uncensored for all weeks and regions except
# S35 (DS).
ORA_sales = np.array(Range('ORA', 'D109:O115', atleast_2d=True).value)
ORA_demand_mat = np.copy(ORA_sales)

# Set ORA prices.
ORA_prices_over_region = np.array(
    Range('pricing', 'D6:D12').value)

ORA_demand = pd.DataFrame(
        {'price': [p for p in ORA_prices_over_region
                   for i in xrange(0, len(months))],
         'region': [region for region in regions
                    for j in xrange(0, len(months))],
         'sales': ORA_sales.ravel(),
         'demand': ORA_demand_mat.ravel()})

ORA_demand.to_csv('ora_demand_2016.csv', index=False)

########
POJ_sales = np.array(Range('POJ', 'D109:O115',
                           atleast_2d=True).value)
POJ_demand_mat = np.copy(POJ_sales)

# Multiply POJ monthly sales by 2 for first month
POJ_demand_mat[:, 0] = POJ_demand_mat[:, 0] * 2

# Set POJ prices.
POJ_prices_over_region = np.array(
    Range('pricing', 'D15:D21').value)

POJ_demand = pd.DataFrame(
        {'price': [p for p in POJ_prices_over_region
                   for i in xrange(0, len(months))],
         'region': [region for region in regions
                    for j in xrange(0, len(months))],
         'sales': POJ_sales.ravel(),
         'demand': POJ_demand_mat.ravel()})

POJ_demand.to_csv('poj_demand_2016.csv', index=False)

######
ROJ_sales = np.array(Range('ROJ', 'D109:O115',
                           atleast_2d=True).value)
ROJ_demand_mat = np.copy(ROJ_sales)

# Multiply ROJ monthly sales by 4/3 for first month.
ROJ_demand_mat[:, 0] = ROJ_demand_mat[:, 0] * 4. / 3

# Set POJ prices.
ROJ_prices_over_region = np.array(
    Range('pricing', 'D24:D30').value)

ROJ_demand = pd.DataFrame(
        {'price': [p for p in ROJ_prices_over_region
                   for i in xrange(0, len(months))],
         'region': [region for region in regions
                    for j in xrange(0, len(months))],
         'sales': ROJ_sales.ravel(),
         'demand': ROJ_demand_mat.ravel()})

ROJ_demand.to_csv('roj_demand_2016.csv', index=False)


######
FCOJ_sales = np.array(Range('FCOJ', 'D109:O115',
                           atleast_2d=True).value)
FCOJ_demand_mat = np.copy(FCOJ_sales)

# S35 and S51 regions are censored
FCOJ_demand_mat[[0, 1, 2, 4], :] = 0

FCOJ_prices_over_region = np.array(
    Range('pricing', 'D33:D39').value)

FCOJ_demand = pd.DataFrame(
        {'price': [p for p in FCOJ_prices_over_region
                   for i in xrange(0, len(months))],
         'region': [region for region in regions
                    for j in xrange(0, len(months))],
         'sales': FCOJ_sales.ravel(),
         'demand': FCOJ_demand_mat.ravel()})

FCOJ_demand.to_csv('fcoj_demand_2016.csv', index=False)
