from xlwings import Workbook, Range
import numpy as np
import pandas as pd

ROOT_DIR = os.path.dirname(os.getcwd())
wb = Workbook(os.path.join(ROOT_DIR, 'reference/StaticData-mod.xlsx'))

# Storage and Markets
storages = Range('S->M', 'C1:BU1').value
markets = ['{0} ({1})'.format(row[1], row[0])
           for row in Range('S->M', 'A2:B101',
                            atleast_2d=True).value]
regions = Range('S->M', 'A2:A101').value
D = np.array(Range('S->M', 'C2:BU101', atleast_2d=True).value)

# [S35, S51, S59, S73], [P02, P03, P05, P09]

dist_df = pd.DataFrame({'region': regions, 'market': markets,
                        'S35_dist': D[:, storages.index('S35')],
                        'S51_dist': D[:, storages.index('S51')],
                        'S59_dist': D[:, storages.index('S59')],
                        'S73_dist': D[:, storages.index('S73')]})
av_dists = dist_df.groupby('region').mean()
av_dists['d'] = np.array(av_dists.min(1))
av_dists.to_csv('region_storage_dists_opt.csv')
