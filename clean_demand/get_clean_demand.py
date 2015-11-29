from xlwings import Workbook, Range
import numpy as np
import pandas as pd
import os

ROOT_DIR = os.path.dirname(os.getcwd())

# Practice round 1 (get all ORA demand)
wb = Workbook(os.path.join(ROOT_DIR,
              'results/notgrapefruit2015 - Practice 1.xlsm'))
price_over_month = np.linspace(1, 4, 12)
months = ['Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar',
          'Apr', 'May', 'Jun', 'Jul', 'Aug']
regions = ['NE', 'MA', 'SE', 'MW', 'DS', 'NW', 'SW']
ORA_sales = np.array(Range('ORA', 'D109:O115', atleast_2d=True).value)

ORA_demand = pd.DataFrame(
        {'price': list(price_over_month) * 7,
         'month': months * len(regions),
         'region': [region for region in regions
                    for j in xrange(0, len(months))],
         'sales': ORA_sales.ravel(),
         'demand': ORA_sales.ravel()})

ORA_demand.to_csv('ora_demand.csv', index=False)


# Practice round 2 (try to get demand for POJ, ROJ, FCOJ)
wb = Workbook(os.path.join(ROOT_DIR,
              'results/notgrapefruit2015 - Practice 2.xlsm'))
price_over_month = np.linspace(4, 1, 12)

## POJ
s15_censoring_POJ = np.array(
    Range('S15', 'D177:AY178', atleast_2d=True).value)
# Uncensored if available > sold
s15_is_censored = [s15_censoring_POJ[0, i] <= s15_censoring_POJ[1, i]
                   for i in xrange(0, s15_censoring_POJ.shape[1])]
s61_censoring_POJ = np.array(
    Range('S61', 'D177:AY178', atleast_2d=True).value)
s61_is_censored = [s61_censoring_POJ[0, i] <= s61_censoring_POJ[1, i]
                   for i in xrange(0, s15_censoring_POJ.shape[1])]
censor_df = pd.DataFrame({'S15_censored': s15_is_censored,
                          'S61_censored': s61_is_censored,
                          'price': [p for p in price_over_month for i in xrange(0, 4)]})
POJ_sales = np.array(Range('POJ', 'D109:O115', atleast_2d=True).value)
POJ_demand_mat = np.copy(POJ_sales)

# First 2 weeks had no available POJ for all regions, so sales in month 1
# should be doubled to approximate $4 (Sept.) demand.
POJ_demand_mat[:, 0] = POJ_demand_mat[:, 0] * 2

# Last 2 months are completely censored for all regions.
POJ_demand_mat[:, 10:12] = 0

# 3rd to last month is half-censored for S15 and fully censored for
# S61.  S61 has NE, MA, SE, and most of MW.  S15 has DS, NW, SW, and
# some of MW.  We zero out the demand for the corresponding S61 regions
# and double the sales for the S15 regions to obtain their estimates
# (let's just assume MW is all S61).
POJ_demand_mat[0:4, 9] = 0
POJ_demand_mat[4:8, 9] = POJ_demand_mat[4:8, 9] * 2

POJ_demand = pd.DataFrame(
        {'price': list(price_over_month) * 7,
         'month': months * len(regions),
         'region': [region for region in regions
                    for j in xrange(0, len(months))],
         'sales': POJ_sales.ravel(),
         'demand': POJ_demand_mat.ravel()})
POJ_demand.to_csv('poj_demand.csv', index=False)

## ROJ
s15_censoring_ROJ = np.array(
    Range('S15', 'D179:AY180', atleast_2d=True).value)
# Uncensored if available > sold
s15_is_censored = [s15_censoring_ROJ[0, i] <= s15_censoring_ROJ[1, i]
                   for i in xrange(0, s15_censoring_ROJ.shape[1])]
s61_censoring_ROJ = np.array(
    Range('S61', 'D179:AY180', atleast_2d=True).value)
s61_is_censored = [s61_censoring_ROJ[0, i] <= s61_censoring_ROJ[1, i]
                   for i in xrange(0, s15_censoring_ROJ.shape[1])]
censor_df = pd.DataFrame({'S15_censored': s15_is_censored,
                          'S61_censored': s61_is_censored,
                          'price': [p for p in price_over_month for i in xrange(0, 4)]})
ROJ_sales = np.array(Range('ROJ', 'D109:O115', atleast_2d=True).value)
ROJ_demand_mat = np.copy(ROJ_sales)

# First 3 weeks had no available ROJ for all regions, so sales in month 1
# should be doubled to approximate $4 (Sept.) demand.
ROJ_demand_mat[:, 0] = ROJ_demand_mat[:, 0] * 4

# Last 2 months are completely censored for all regions.
ROJ_demand_mat[:, 10:12] = 0

# 3rd to last month is half-censored for S15 and S61.
# S61.  S61 has NE, MA, SE, and most of MW.  S15 has DS, NW, SW, and
# some of MW.  We zero out the demand for the corresponding S61 regions
# and double the sales for the S15 regions to obtain their estimates
# (let's just assume MW is all S61).
ROJ_demand_mat[:, 9] = ROJ_demand_mat[:, 9] * 2

ROJ_demand = pd.DataFrame(
        {'price': list(price_over_month) * 7,
         'month': months * len(regions),
         'region': [region for region in regions
                    for j in xrange(0, len(months))],
         'sales': ROJ_sales.ravel(),
         'demand': ROJ_demand_mat.ravel()})
ROJ_demand.to_csv('roj_demand.csv', index=False)

## FCOJ
s15_censoring_FCOJ = np.array(
    Range('S15', 'D181:AY182', atleast_2d=True).value)
# Uncensored if available > sold
s15_is_censored = [s15_censoring_FCOJ[0, i] <= s15_censoring_FCOJ[1, i]
                   for i in xrange(0, s15_censoring_FCOJ.shape[1])]
s61_censoring_FCOJ = np.array(
    Range('S61', 'D181:AY182', atleast_2d=True).value)
s61_is_censored = [s61_censoring_FCOJ[0, i] <= s61_censoring_FCOJ[1, i]
                   for i in xrange(0, s15_censoring_FCOJ.shape[1])]
censor_df = pd.DataFrame({'S15_censored': s15_is_censored,
                          'S61_censored': s61_is_censored,
                          'price': [p for p in price_over_month for i in xrange(0, 4)]})
FCOJ_sales = np.array(Range('FCOJ', 'D109:O115', atleast_2d=True).value)
FCOJ_demand_mat = np.copy(FCOJ_sales)

# First 3 weeks had no available ROJ for all regions, so sales in month 1
# should be doubled to approximate $4 (Sept.) demand.
FCOJ_demand_mat[:, 0] = FCOJ_demand_mat[:, 0] * 4

# Last 3 months are completely censored for all regions.
FCOJ_demand_mat[:, 9:12] = 0

# 3rd to last month is half-censored for S15 and S61.
# S61.  S61 has NE, MA, SE, and most of MW.  S15 has DS, NW, SW, and
# some of MW.  We zero out the demand for the corresponding S61 regions
# and double the sales for the S15 regions to obtain their estimates
# (let's just assume MW is all S61).
FCOJ_demand_mat[0:4, 8] = FCOJ_demand_mat[0:4, 8] * 2
FCOJ_demand_mat[4:8, 8] = FCOJ_demand_mat[4:8, 8] * 4 / 3

FCOJ_demand_mat[4:8, 7] = FCOJ_demand_mat[4:8, 7] * 2

FCOJ_demand = pd.DataFrame(
        {'price': list(price_over_month) * 7,
         'month': months * len(regions),
         'region': [region for region in regions
                    for j in xrange(0, len(months))],
         'sales': FCOJ_sales.ravel(),
         'demand': FCOJ_demand_mat.ravel()})
FCOJ_demand.to_csv('fcoj_demand.csv', index=False)