from xlwings import Workbook, Range
import numpy as np
import pandas as pd
import os
import sys

latest_year = int(sys.argv[1])

# directory setup
ROOT_DIR = os.path.dirname(os.getcwd())

YEARS = list(xrange(2019, latest_year + 1))
ORA_betas = [None] * len(YEARS)
POJ_betas = [None] * len(YEARS)
ROJ_betas = [None] * len(YEARS)
FCOJ_betas = [None] * len(YEARS)

for i, year in enumerate(YEARS):
    init_wb = Workbook(
        os.path.join(ROOT_DIR,
                     'decisions/notgrapefruit{0}_init.xlsm'.format(year)),
                     app_visible=False)
    ORA_init_prices = np.array(Range('pricing', 'D6:O12', atleast_2d=True).value)
    POJ_init_prices = np.array(Range('pricing', 'D15:O21', atleast_2d=True).value)
    ROJ_init_prices = np.array(Range('pricing', 'D24:O30', atleast_2d=True).value)
    FCOJ_init_prices = np.array(Range('pricing', 'D33:O39', atleast_2d=True).value)
    init_wb.close()

    tuned_wb = Workbook(
        os.path.join(ROOT_DIR,
                     'decisions/notgrapefruit{0}.xlsm'.format(year)),
                     app_visible=False)
    ORA_tuned_prices = np.array(Range('pricing', 'D6:O12', atleast_2d=True).value)
    POJ_tuned_prices = np.array(Range('pricing', 'D15:O21', atleast_2d=True).value)
    ROJ_tuned_prices = np.array(Range('pricing', 'D24:O30', atleast_2d=True).value)
    FCOJ_tuned_prices = np.array(Range('pricing', 'D33:O39', atleast_2d=True).value)

    ORA_betas[i] = ORA_tuned_prices - ORA_init_prices
    POJ_betas[i] = POJ_tuned_prices - POJ_init_prices
    ROJ_betas[i] = ROJ_tuned_prices - ROJ_init_prices
    FCOJ_betas[i] = FCOJ_tuned_prices - FCOJ_init_prices

ORA_beta_beliefs = sum(ORA_betas) / len(YEARS)
POJ_beta_beliefs = sum(POJ_betas) / len(YEARS)
ROJ_beta_beliefs = sum(ROJ_betas) / len(YEARS)
FCOJ_beta_beliefs = sum(FCOJ_betas) / len(YEARS)

np.savetxt('price_adjustments/ORA_beta.csv', ORA_beta_beliefs, delimiter=",")
np.savetxt('price_adjustments/POJ_beta.csv', POJ_beta_beliefs, delimiter=",")
np.savetxt('price_adjustments/ROJ_beta.csv', ROJ_beta_beliefs, delimiter=",")
np.savetxt('price_adjustments/FCOJ_beta.csv', FCOJ_beta_beliefs, delimiter=",")