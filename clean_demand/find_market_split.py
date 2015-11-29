from xlwings import Workbook, Range
import numpy as np
import pandas as pd
import os

ROOT_DIR = os.path.dirname(os.getcwd())
wb = Workbook(os.path.join(ROOT_DIR, 'reference/StaticData-mod.xlsx'))

# Storage and Markets
storages = Range('S->M', 'C1:BU1').value
markets = Range('S->M', 'B2:B101').value
regions = Range('S->M', 'A2:A101').value
D = np.array(Range('S->M', 'C2:BU101', atleast_2d=True).value)

opt_storages = ['S35', 'S51', 'S59', 'S73']
i = storages.index('S35')
j = storages.index('S51')
k = storages.index('S59')
l = storages.index('S73')

min_dists = [min(D[r, i], D[r, j], D[r, k], D[r, l])
             for r in xrange(0, len(D))]
closest_storage_ind = [[D[r, i], D[r, j], D[r, k], D[r, l]].index(
    min(D[r, i], D[r, j], D[r, k], D[r, l])) for r in xrange(0, len(D))]
closest_df = pd.DataFrame(
    {'market': markets,
     'region': regions,
     'closest_storage': [opt_storages[s]
                         for s in closest_storage_ind]})
