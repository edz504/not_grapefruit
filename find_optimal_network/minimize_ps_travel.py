from xlwings import Workbook, Range
import numpy as np
import pandas as pd
import os
import itertools

ROOT_DIR = os.path.dirname(os.getcwd())
wb = Workbook(os.path.join(ROOT_DIR, 'reference/StaticData-mod.xlsx'))

# Storage and Plants
storages = Range('P->S', 'A2:A72').value
plants = Range('P->S', 'B1:K1').value
D = np.array(Range('P->S', 'B2:K72', atleast_2d=True).value)

# Only include the 4 storages from previous analysis.
storages_fixed = (u'S35', u'S51', u'S59', u'S73')
D_fixed = D[[storages.index(s) for s in storages_fixed], :]

# Seek to minimize the sum of the distance from each storage
# to its closest open processing plant.

# P = 1
total_distances = {}
for p in xrange(0, D_fixed.shape[1]):
    total_distances[p] = sum(D_fixed[:, p])
best = min(total_distances, key=total_distances.get)

# Return set of best plants for a given plant size P, as well as
# total distance for that plant size P.
def get_best_plants(P):
    combs = list(itertools.combinations(xrange(0, len(plants)), P))
    total_distances = {}
    for c in combs:
        dists = np.array([list(D_fixed[:, i]) for i in c])
        total_distances[c] = sum(np.amin(dists, axis=0))
    best = min(total_distances, key=total_distances.get)
    return (best, total_distances[best])

for P in xrange(1, 11):
    best, dist = get_best_plants(P)
    best_names = [str(plants[b]) for b in best]
    print ('''P = {0}, best set is {1}, '''
           '''for a total d = {2}''').format(P, best_names, dist)