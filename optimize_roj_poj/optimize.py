import numpy as np
import pandas as pd
import os

ROOT_DIR = os.path.dirname(os.getcwd())
df = pd.read_csv(os.path.join(ROOT_DIR,
    'fit_demand/demand_fit_coefs.csv'))

def cube_root(x):
    return math.pow(abs(x), float(1) / 3) * (1,-1)[x < 0]

# P2 (DS)
# R + P = 855
this_roj_df = df[(df['region'] == 'DS') & (df['product'] == 'ROJ')]
this_poj_df = df[(df['region'] == 'DS') & (df['product'] == 'POJ')]
obj = [None] * 856
p_P_vec = [None] * 856
p_R_vec = [None] * 856
for R in xrange(0, 856):
    p_R = 2000 * cube_root(float(this_roj_df['c1'] / (R - this_roj_df['intercept'])))
    c_R = 1650

    P = 855 - R
    p_P = 2000 * cube_root(float(this_poj_df['c1'] / (P - this_poj_df['intercept'])))
    c_P = 2000
    obj[R] = float(R * (p_R - c_R)) + float(P * (p_P - c_P))
    p_P_vec[R] = float(p_P) / 2000
    p_R_vec[R] = float(p_R) / 2000

opt_df = pd.DataFrame({'R': xrange(0, 856),
                       'obj': obj,
                       'POJ_price_per_lb': p_P_vec,
                       'ROJ_price_per_lb': p_R_vec})
opt_df.to_csv('p02_optimization.csv', index=False)
argmax = obj.index(max(obj))
print 'For P02 (region DS), objective maximization is at'
print 'R = {0} ($/lb = {1}), P = {2} ($/lb = {3})'.format(
    argmax, opt_df['ROJ_price_per_lb'][argmax],
    855 - argmax, opt_df['POJ_price_per_lb'][argmax])


# P9 (MW)
# R + P = 645
this_roj_df = df[(df['region'] == 'MW') & (df['product'] == 'ROJ')]
this_poj_df = df[(df['region'] == 'MW') & (df['product'] == 'POJ')]
obj = [None] * 646
p_P_vec = [None] * 646
p_R_vec = [None] * 646
for R in xrange(0, 646):
    p_R = 2000 * (this_roj_df['c1'] / (R - this_roj_df['intercept'])) ** (1./3)
    c_R = 1650

    P = 645 - R
    p_P = 2000 * (this_poj_df['c1'] / (P - this_poj_df['intercept'])) ** (1./3)
    c_P = 2000

    obj[R] = float(R * (p_R - c_R)) + float(P * (p_P - c_P))
    p_P_vec[R] = float(p_P) / 2000
    p_R_vec[R] = float(p_R) / 2000

opt_df = pd.DataFrame({'R': xrange(0, 646),
                       'obj': obj,
                       'POJ_price_per_lb': p_P_vec,
                       'ROJ_price_per_lb': p_R_vec})
opt_df.to_csv('p09_optimization.csv', index=False)
argmax = obj.index(max(obj))
print 'For P09 (region MW), objective maximization is at'
print 'R = {0} ($/lb = {1}), P = {2} ($/lb = {3})'.format(
    argmax, opt_df['ROJ_price_per_lb'][argmax],
    645 - argmax, opt_df['POJ_price_per_lb'][argmax])




# How do we do this for multi-region plants?
# For a range of prices from 1 to 4, calculate the demand from the
# regions.  Then, for a given value of R, we can find the price that
# creates a total demand closest to D1 + D2.  This turns the parametrized
# demand estimation from the SW and NW regions into a look-up table.

# P5 (SW, NW)
# R + P = 885
p_vec = np.linspace(1, 4, 1000)
P05_ROJ_demand = [None] * len(p_vec)
P05_POJ_demand = [None] * len(p_vec)
for i, p in enumerate(p_vec):
    SW_ROJ_values = df[(df['region'] == 'SW') & (df['product'] == 'ROJ')]
    SW_ROJ_demand = SW_ROJ_values['c1'] / (p ** 3) + SW_ROJ_values['intercept']
    NW_ROJ_values = df[(df['region'] == 'NW') & (df['product'] == 'ROJ')]
    NW_ROJ_demand = NW_ROJ_values['c1'] / (p ** 3) + NW_ROJ_values['intercept']
    P05_ROJ_demand[i] = float(SW_ROJ_demand) + float(NW_ROJ_demand)

    SW_POJ_values = df[(df['region'] == 'SW') & (df['product'] == 'POJ')]
    SW_POJ_demand = SW_POJ_values['c1'] / (p ** 3) + SW_POJ_values['intercept']
    NW_POJ_values = df[(df['region'] == 'NW') & (df['product'] == 'POJ')]
    NW_POJ_demand = NW_POJ_values['c1'] / (p ** 3) + NW_POJ_values['intercept']
    P05_POJ_demand[i] = float(SW_POJ_demand) + float(NW_POJ_demand)

P05_demand_df = pd.DataFrame({'price': p_vec,
                              'ROJ_demand': P05_ROJ_demand,
                              'POJ_demand': P05_POJ_demand})
obj = [None] * 886
p_P_vec = [None] * 886
p_R_vec = [None] * 886
for R in xrange(0, 886):
    p_R = 2000 * p_vec[
        list(P05_demand_df['ROJ_demand']).index(
             min(P05_demand_df['ROJ_demand'],
             key=lambda x : abs(x - R)))]
    c_R = 1650

    P = 885 - R
    p_P = 2000 * p_vec[
        list(P05_demand_df['POJ_demand']).index(
             min(P05_demand_df['POJ_demand'],
             key=lambda x : abs(x - P)))]
    c_P = 2000
    obj[R] = float(R * (p_R - c_R)) + float(P * (p_P - c_P))
    p_P_vec[R] = float(p_P) / 2000
    p_R_vec[R] = float(p_R) / 2000

opt_df = pd.DataFrame({'R': xrange(0, 886),
                       'obj': obj,
                       'POJ_price_per_lb': p_P_vec,
                       'ROJ_price_per_lb': p_R_vec})
opt_df.to_csv('p05_optimization.csv', index=False)
argmax = obj.index(max(obj))
print 'For P05 (regions SW, NW), objective maximization is at'
print 'R = {0} ($/lb = {1}), P = {2} ($/lb = {3})'.format(
    argmax, opt_df['ROJ_price_per_lb'][argmax],
    885 - argmax, opt_df['POJ_price_per_lb'][argmax])

# P3 (SE, MA, NE)
# R + P = 2730
p_vec = np.linspace(1, 4, 1000)
P03_ROJ_demand = [None] * len(p_vec)
P03_POJ_demand = [None] * len(p_vec)
for i, p in enumerate(p_vec):
    SE_ROJ_values = df[(df['region'] == 'SE') & (df['product'] == 'ROJ')]
    SE_ROJ_demand = SE_ROJ_values['c1'] / (p ** 3) + SE_ROJ_values['intercept']
    MA_ROJ_values = df[(df['region'] == 'MA') & (df['product'] == 'ROJ')]
    MA_ROJ_demand = MA_ROJ_values['c1'] / (p ** 3) + MA_ROJ_values['intercept']
    NE_ROJ_values = df[(df['region'] == 'NE') & (df['product'] == 'ROJ')]
    NE_ROJ_demand = NE_ROJ_values['c1'] / (p ** 3) + NE_ROJ_values['intercept']
    P03_ROJ_demand[i] = float(SE_ROJ_demand) + float(MA_ROJ_demand) + float(NE_ROJ_demand)

    SE_POJ_values = df[(df['region'] == 'SE') & (df['product'] == 'POJ')]
    SE_POJ_demand = SE_POJ_values['c1'] / (p ** 3) + SE_POJ_values['intercept']
    MA_POJ_values = df[(df['region'] == 'MA') & (df['product'] == 'POJ')]
    MA_POJ_demand = MA_POJ_values['c1'] / (p ** 3) + MA_POJ_values['intercept']
    NE_POJ_values = df[(df['region'] == 'NE') & (df['product'] == 'POJ')]
    NE_POJ_demand = NE_POJ_values['c1'] / (p ** 3) + NE_POJ_values['intercept']
    P03_POJ_demand[i] = float(SE_POJ_demand) + float(MA_POJ_demand) + float(NE_POJ_demand)

P03_demand_df = pd.DataFrame({'price': p_vec,
                              'ROJ_demand': P03_ROJ_demand,
                              'POJ_demand': P03_POJ_demand})
obj = [None] * 2731
p_P_vec = [None] * 2731
p_R_vec = [None] * 2731
for R in xrange(0, 2731):
    p_R = 2000 * p_vec[
        list(P03_demand_df['ROJ_demand']).index(
             min(P03_demand_df['ROJ_demand'],
             key=lambda x : abs(x - R)))]
    c_R = 1650

    P = 2730 - R
    p_P = 2000 * p_vec[
        list(P03_demand_df['POJ_demand']).index(
             min(P03_demand_df['POJ_demand'],
             key=lambda x : abs(x - P)))]
    c_P = 2000
    obj[R] = float(R * (p_R - c_R)) + float(P * (p_P - c_P))
    p_P_vec[R] = float(p_P) / 2000
    p_R_vec[R] = float(p_R) / 2000

opt_df = pd.DataFrame({'R': xrange(0, 2731),
                       'obj': obj,
                       'POJ_price_per_lb': p_P_vec,
                       'ROJ_price_per_lb': p_R_vec})
opt_df.to_csv('p03_optimization.csv', index=False)
argmax = obj.index(max(obj))
print 'For P03 (regions NE, MA, SE), objective maximization is at'
print 'R = {0} ($/lb = {1}), P = {2} ($/lb = {3})'.format(
    argmax, opt_df['ROJ_price_per_lb'][argmax],
    2730 - argmax, opt_df['POJ_price_per_lb'][argmax])