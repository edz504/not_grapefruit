from xlwings import Workbook, Range
import numpy as np
import pandas as pd
import os

ROOT_DIR = os.path.dirname(os.getcwd())
wb = Workbook(os.path.join(ROOT_DIR, 'reference/StaticData-mod.xlsx'))

# Storage and Markets
storages = Range('S->M', 'C1:BU1').value
markets = ['{0} ({1})'.format(row[1], row[0])
           for row in Range('S->M', 'A2:B101',
                            atleast_2d=True).value]
D = np.array(Range('S->M', 'C2:BU101', atleast_2d=True).value)



# Could do this recursively / with DP but this is quicker.
# S = 1
total_distances = {}
for s in xrange(0, D.shape[1]):
    total_distances[s] = sum(D[:, s])
best = min(total_distances, key=total_distances.get)

# S = 2
total_distances_2 = {}
for i in xrange(0, D.shape[1]):
    for j in xrange(i + 1, D.shape[1]):
        min_dists = [min(D[r, i], D[r, j])
                     for r in xrange(0, len(D))]
        total_distances_2[(storages[i],
            storages[j])] = sum(min_dists)
best2 = min(total_distances_2, key=total_distances_2.get)

# S = 3
total_distances_3 = {}
for i in xrange(0, D.shape[1]):
    for j in xrange(i + 1, D.shape[1]):
        for k in xrange(j + 1, D.shape[1]):
            min_dists = [min(D[r, i], D[r, j], D[r, k])
                         for r in xrange(0, len(D))]
            total_distances_3[(storages[i],
                storages[j], storages[k])] = sum(min_dists)
best3 = min(total_distances_3, key=total_distances_3.get)

# S = 4
total_distances_4 = {}
for i in xrange(0, D.shape[1]):
    for j in xrange(i + 1, D.shape[1]):
        for k in xrange(j + 1, D.shape[1]):
            for l in xrange(k + 1, D.shape[1]):
                min_dists = [min(D[r, i], D[r, j], D[r, k],
                                 D[r, l])
                             for r in xrange(0, len(D))]
                total_distances_4[(storages[i],
                    storages[j], storages[k],
                    storages[l])] = sum(min_dists)
best4 = min(total_distances_4, key=total_distances_4.get)


print ('''S = 1: {0} gives the '''
       '''min total dist to markets = {1}''').format(
        storages[best], total_distances[best])
print ('''S = 2: {0} gives the '''
       '''min total dist to markets = {1}''').format(
        best2, total_distances_2[best2])
print ('''S = 3: {0} gives the '''
       '''min total dist to markets = {1}''').format(
        best3, total_distances_3[best3])
print ('''S = 4: {0} gives the '''
       '''min total dist to markets = {1}''').format(
        best4, total_distances_4[best4])

opt_sm = {1: (best, total_distances[best]),
          2: (best2, total_distances_2[best2]),
          3: (best3, total_distances_3[best3]),
          4: (best4, total_distances_4[best4])}
import cPickle as pickle
with open('opt_sm.pkl', 'wb') as f:
    pickle.dump(opt_sm, f)


# current storage system4
i = storages.index('S15')
j = storages.index('S61')
total_distance = sum([min(D[r, i], D[r, j])
                      for r in xrange(0, len(D))])


# Check 4th week of May transportation costs
dists = [min(D[m, storages.index('S15')],
             D[m, storages.index('S61')])
         for m in xrange(0, len(markets))]

wb = Workbook(os.path.join(os.getcwd(),
    'Results/notgrapefruit2015 - Practice 2.xlsm'))

sales = Range('POJ', 'BV6:BV105').value
cost = sum(1.2 * d * s for d, s in zip(dists, sales))

# Compute assumed transportation costs (see minimize_travel_results.txt)
total_D_vec = [77741, 64774, 52687, 45887]
print [1.2 * (total_d / 100) * 100 * (50 + 40 + 35 + 30) * 48
       for total_d in total_D_vec]