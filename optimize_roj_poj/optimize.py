import numpy as np
import pandas as pd
import os

ROOT_DIR = os.path.dirname(os.getcwd())
df = pd.read_csv(os.path.join(ROOT_DIR,
    'clean_demand/demand_fit_coefs.csv'))

# P2 (DS)
# R + P = 855
this_roj_df = df[(df['region'] == 'DS') & (df['product'] == 'ROJ')]
this_poj_df = df[(df['region'] == 'DS') & (df['product'] == 'POJ')]
obj = [None] * 856
for R in xrange(0, 856):
    p_R = 2000 * np.sqrt(
        this_roj_df['c1'] / (R - this_roj_df['intercept']))
    c_R = 1650

    P = 855 - R
    p_P = 2000 * np.sqrt(
        this_poj_df['c1'] / (P - this_poj_df['intercept']))
    c_P = 2000
    obj[R] = float(R * (p_R - c_R)) + float(P * (p_P - c_P))

pd.DataFrame({'R': xrange(0, 856),
              'obj': obj}).to_csv('p02_optimization.csv', index=False)

# P9 (MW)
# R + P = 645
this_roj_df = df[(df['region'] == 'MW') & (df['product'] == 'ROJ')]
this_poj_df = df[(df['region'] == 'MW') & (df['product'] == 'POJ')]
obj = [None] * 646
for R in xrange(0, 646):
    p_R = 2000 * np.sqrt(
        this_roj_df['c1'] / (R - this_roj_df['intercept']))
    c_R = 1650

    P = 645 - R
    p_P = 2000 * np.sqrt(
        this_poj_df['c1'] / (P - this_poj_df['intercept']))
    c_P = 2000

    obj[R] = float(R * (p_R - c_R)) + float(P * (p_P - c_P))

pd.DataFrame({'R': xrange(0, 646),
              'obj': obj}).to_csv('p09_optimization.csv', index=False)



### Need to fix this

# P3 (SE, MA, NE)
# R + P = 2730
this_roj_df = df[((df['region'] == 'NE') | (df['region'] == 'MA') |
                  (df['region'] == 'SE')) & (df['product'] == 'ROJ')]
this_poj_df = df[(df['region'] == 'DS') & (df['product'] == 'POJ')]
obj = [None] * 2731
for R in xrange(0, 2731):
    p_R = (R - this_roj_df['intercept']) / this_roj_df['c1'] * 2000
    c_R = 1650

    P = 855 - R
    p_P = (P - this_poj_df['intercept']) / this_poj_df['c1'] * 2000
    c_P = 2000

    obj[R] = float(R * (p_R - c_R)) + float(P * (p_P - c_P))

pd.DataFrame({'R': xrange(0, 2731),
              'obj': obj}).to_csv('p02_optimization.csv', index=False)