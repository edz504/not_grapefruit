from xlwings import Workbook, Range
import numpy as np
import pandas as pd
import os
import shutil
import sys

YEAR = sys.argv[1]

# directory setup
ROOT_DIR = os.path.dirname(os.getcwd())

# Get initialized workbook.
wb = Workbook(
    os.path.join(ROOT_DIR,
                 'decisions/notgrapefruit{0}_init.xlsm'.format(YEAR)),
    app_visible=False)

ORA_beta_beliefs = np.genfromtxt('price_adjustments/ORA_beta.csv', delimiter=',')
POJ_beta_beliefs = np.genfromtxt('price_adjustments/POJ_beta.csv', delimiter=',')
ROJ_beta_beliefs = np.genfromtxt('price_adjustments/ROJ_beta.csv', delimiter=',')
FCOJ_beta_beliefs = np.genfromtxt('price_adjustments/FCOJ_beta.csv', delimiter=',')

ORA_adjusted = np.array(Range('pricing', 'D6:O12', atleast_2d=True).value) + ORA_beta_beliefs
POJ_adjusted = np.array(Range('pricing', 'D15:O21', atleast_2d=True).value) + POJ_beta_beliefs
ROJ_adjusted = np.array(Range('pricing', 'D24:O30', atleast_2d=True).value) + ROJ_beta_beliefs
FCOJ_adjusted = np.array(Range('pricing', 'D33:O39', atleast_2d=True).value) + FCOJ_beta_beliefs

wb.close()

wb = Workbook(
    os.path.join(ROOT_DIR,
                 'decisions/notgrapefruit{0}.xlsm'.format(YEAR)),
    app_visible=False)

Range('pricing', 'D6:O12', atleast_2d=True).value = ORA_adjusted
Range('pricing', 'D15:O21', atleast_2d=True).value = POJ_adjusted
Range('pricing', 'D24:O30', atleast_2d=True).value = ROJ_adjusted
Range('pricing', 'D33:O39', atleast_2d=True).value = FCOJ_adjusted

wb.save()
wb.close()
