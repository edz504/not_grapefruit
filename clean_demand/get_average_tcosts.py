from xlwings import Workbook, Range
import numpy as np
import pandas as pd

wb = Workbook('/Users/edz/Documents/Princeton/Senior/ORF411/OJ/Analysis/StaticData-mod.xlsx')

# Storage and Markets
storages = Range('S->M', 'C1:BU1').value
markets = ['{0} ({1})'.format(row[1], row[0])
           for row in Range('S->M', 'A2:B101',
                            atleast_2d=True).value]
regions = Range('S->M', 'A2:A101').value
D = np.array(Range('S->M', 'C2:BU101', atleast_2d=True).value)

dist_df = pd.DataFrame({'region': regions, 'market': markets,
                        'S15_dist': D[:, storages.index('S15')],
                        'S61_dist': D[:, storages.index('S61')]})
av_dists = dist_df.groupby('region').mean()
av_dists['d'] = np.array(av_dists.min(1))
av_dists.to_csv('region_storage_dists.csv')

