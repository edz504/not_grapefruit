from xlwings import Workbook, Range
import numpy as np
import pandas as pd
import os

# directory setup
ROOT_DIR = os.path.dirname(os.getcwd())

# Set up workbook to write to.
wb = Workbook(
    os.path.join(ROOT_DIR,
                 'decisions/notgrapefruit2019.xlsm'),
              app_visible=False)


# Change when we switch plans
ora = pd.read_csv('profit_csvs/ora_max_profit.csv')
poj = pd.read_csv('profit_csvs/poj_max_profit.csv')
roj = pd.read_csv('profit_csvs/roj_max_profit.csv')
# roj = pd.read_csv('profit_csvs/roj_futures_max_profit.csv')
fcoj = pd.read_csv('profit_csvs/fcoj_fixed_quantity.csv')
# fcoj = pd.read_csv('profit_csvs/fcoj_futures_max_profit.csv')

df = pd.concat([ora.iloc[:, :4],
                poj.iloc[:, :4],
                roj.iloc[:, :4],
                fcoj.iloc[:, :4]])

by_region = df.groupby('region').aggregate(
            {'predicted_demand': sum})

# These are sanity checks to make sure our current storage is
# above these capacity demands.
print 'S51 storage capacity needed: {0}'.format(
    sum(by_region.loc[['NE', 'MA', 'SE']]['predicted_demand']))
print 'S35 storage capacity needed: {0}'.format(
    float(by_region.loc['DS']))
print 'S59 storage capacity: {0}'.format(
    sum(by_region.loc[['NW', 'SW']]['predicted_demand']))
print 'S73 storage capacity needed: {0}'.format(
    float(by_region.loc['MW']))

# Same thing for processing.  Note that we only care about
# POJ amount processed (and ROJ for 2019 and 2020, before
# we convert to using futures for ROJ also).
by_region_proc = df[(df['product'] == 'POJ') |
                    (df['product'] == 'ROJ')].groupby(
                        'region').aggregate(
                        {'predicted_demand': sum})
# by_region_proc = df[(df['product'] == 'POJ')].groupby(
#                         'region').aggregate(
#                         {'predicted_demand': sum})
print 'P03 processing capacity needed: {0}'.format(
    sum(by_region_proc.loc[['NE', 'MA', 'SE']]['predicted_demand']))
print 'P02 processing capacity needed: {0}'.format(
    float(by_region_proc.loc['DS']))
print 'P05 processing capacity: {0}'.format(
    sum(by_region_proc.loc[['NW', 'SW']]['predicted_demand']))
print 'P09 processing capacity needed: {0}'.format(
    float(by_region_proc.loc['MW']))

### Spot purchase quantities.
# FLA weekly spot purchase
fla = df[((df['region'] == 'NE') |
          (df['region'] == 'MA') |
          (df['region'] == 'SE') |
          (df['region'] == 'MW')) &
         ((df['product'] == 'ORA') |
          (df['product'] == 'POJ') |
          (df['product'] == 'ROJ'))]
# remove ROJ once transition
Range('raw_materials', 'C6:N6').value = [
    sum(fla['predicted_demand'])] * 12

# CAL weekly spot purchase
cal = df[((df['region'] == 'SW') |
          (df['region'] == 'NW')) &
         ((df['product'] == 'ORA') |
          (df['product'] == 'POJ') |
          (df['product'] == 'ROJ'))]
Range('raw_materials', 'C7:N7').value = [
    sum(cal['predicted_demand'])] * 12

# TEX weekly spot purchase
tex = df[(df['region'] == 'DS') &
         ((df['product'] == 'ORA') |
          (df['product'] == 'POJ') |
          (df['product'] == 'ROJ'))]
Range('raw_materials', 'C8:N8').value = [
    sum(tex['predicted_demand'])] * 12

### Multipliers
# No multipliers.
Range('raw_materials',
      'C17:H22',
      atleast_2d=True).value = np.matrix(
      '''1   0.6 1   1.5 0   1000000;
         1   0.65    1   1.5 0   1000000;
         1   0.72    1   1.5 0   1000000;
         1   1000000 1   1000000 1   1000000;
         1   1000000 1   1000000 1   1000000;
         1   1000000 1   1000000 1   1000000''')

###s Calculate 5-year futures to order
roj_futures = pd.read_csv(
    'profit_csvs/roj_futures_max_profit.csv')
fcoj_futures = pd.read_csv(
    'profit_csvs/fcoj_futures_max_profit.csv')
Range('raw_materials', 'O41').value = sum(
    roj_futures['predicted_demand'] +
    fcoj_futures['predicted_demand']) * 48

### Write in the arrivals
# Even distribution.
Range('raw_materials',
      'C47:N48',
      atleast_2d=True).value = np.matrix(
      [[100. / 12] * 24, [100. / 12] * 24])


### Calculate grove shipping proportions
# Remember to remove ROJ from processing once we transition.
# FLA to P03
Range('shipping_manufacturing', 'D6').value = (
    sum(df[((df['region'] == 'NE') |
            (df['region'] == 'MA') |
            (df['region'] == 'SE')) &
           ((df['product'] == 'POJ') |
            (df['product'] == 'ROJ'))]['predicted_demand']) /
    sum(fla['predicted_demand'])) * 100

# FLA to P09
Range('shipping_manufacturing', 'F6').value = (
    sum(df[(df['region'] == 'MW') &
           ((df['product'] == 'POJ') |
            (df['product'] == 'ROJ'))]['predicted_demand']) /
    sum(fla['predicted_demand'])) * 100

# FLA to S51
Range('shipping_manufacturing', 'H6').value = (
    sum(df[((df['region'] == 'NE') |
            (df['region'] == 'MA') |
            (df['region'] == 'SE')) &
           (df['product'] == 'ORA')]['predicted_demand']) /
    sum(fla['predicted_demand'])) * 100

# FLA to S73
Range('shipping_manufacturing', 'J6').value = (
    sum(df[(df['region'] == 'MW') &
           (df['product'] == 'ORA')]['predicted_demand']) /
    sum(fla['predicted_demand'])) * 100

# CAL to P05
Range('shipping_manufacturing', 'E7').value = (
    sum(df[((df['region'] == 'NW') |
            (df['region'] == 'SW')) &
           ((df['product'] == 'POJ') |
            (df['product'] == 'ROJ'))]['predicted_demand']) /
    sum(cal['predicted_demand'])) * 100

# CAL to S59
Range('shipping_manufacturing', 'I7').value = (
    sum(df[((df['region'] == 'NW') |
            (df['region'] == 'SW')) &
           (df['product'] == 'ORA')]['predicted_demand']) /
    sum(cal['predicted_demand'])) * 100

# TEX to P02
Range('shipping_manufacturing', 'C8').value = (
    sum(df[(df['region'] == 'DS') &
           ((df['product'] == 'POJ') |
            (df['product'] == 'ROJ'))]['predicted_demand']) /
    sum(tex['predicted_demand'])) * 100

# TEX to S35
Range('shipping_manufacturing', 'G8').value = (
    sum(df[(df['region'] == 'DS') &
           (df['product'] == 'ORA')]['predicted_demand']) /
    sum(tex['predicted_demand'])) * 100

# Fill in others
Range('shipping_manufacturing',
      'C9:C11',
      atleast_2d=True).value = np.matrix('100;100;100')

### Manufacturing ratios
# This is unnecessary once we transition (write all 100% POJ).
# P02
Range('shipping_manufacturing', 'C19').value = (
    sum(df[(df['region'] == 'DS') &
           (df['product'] == 'POJ')]['predicted_demand']) /
    sum(df[(df['region'] == 'DS') &
           ((df['product'] == 'POJ') |
            (df['product'] == 'ROJ'))]['predicted_demand'])) * 100

# P03
Range('shipping_manufacturing', 'E19').value = (
    sum(df[((df['region'] == 'NE') |
            (df['region'] == 'MA') |
            (df['region'] == 'SE')) &
           (df['product'] == 'POJ')]['predicted_demand']) /
    sum(df[((df['region'] == 'NE') |
            (df['region'] == 'MA') |
            (df['region'] == 'SE')) &
           ((df['product'] == 'POJ') |
            (df['product'] == 'ROJ'))]['predicted_demand'])) * 100

# P05
Range('shipping_manufacturing', 'G19').value = (
    sum(df[((df['region'] == 'NW') |
            (df['region'] == 'SW')) &
           (df['product'] == 'POJ')]['predicted_demand']) /
    sum(df[((df['region'] == 'NW') |
            (df['region'] == 'SW')) &
           ((df['product'] == 'POJ') |
            (df['product'] == 'ROJ'))]['predicted_demand'])) * 100

# P09
Range('shipping_manufacturing', 'I19').value = (
    sum(df[(df['region'] == 'MW') &
           (df['product'] == 'POJ')]['predicted_demand']) /
    sum(df[(df['region'] == 'MW') &
           ((df['product'] == 'POJ') |
            (df['product'] == 'ROJ'))]['predicted_demand'])) * 100

### Futures shipping ratios
# After transition, product should be both FCOJ and ROJ demand
# S35
Range('shipping_manufacturing', 'C27').value = (
    sum(df[(df['region'] == 'DS') &
           (df['product'] == 'FCOJ')]['predicted_demand']) /
    sum(df[(df['product'] == 'FCOJ')]['predicted_demand'])) * 100
# S51
Range('shipping_manufacturing', 'C28').value = (
    sum(df[((df['region'] == 'NE') |
            (df['region'] == 'MA') |
            (df['region'] == 'SE')) &
           (df['product'] == 'FCOJ')]['predicted_demand']) /
    sum(df[(df['product'] == 'FCOJ')]['predicted_demand'])) * 100
# S59
Range('shipping_manufacturing', 'C29').value = (
    sum(df[((df['region'] == 'NW') |
            (df['region'] == 'SW')) &
           (df['product'] == 'FCOJ')]['predicted_demand']) /
    sum(df[(df['product'] == 'FCOJ')]['predicted_demand'])) * 100
# S73
Range('shipping_manufacturing', 'C30').value = (
    sum(df[(df['region'] == 'MW') &
           (df['product'] == 'FCOJ')]['predicted_demand']) /
    sum(df[(df['product'] == 'FCOJ')]['predicted_demand'])) * 100

# 1-to-1 storage to processing plant for shipping
Range('shipping_manufacturing',
      'D27:K30',
      atleast_2d=True).value = np.matrix(
      '''100   100 0   0   0   0   0   0;
         0   0   100 100 0   0   0   0;
         0   0   0   0   100 100 0   0;
         0   0   0   0   0   0   100 100''')

### Reconstitution
# S35
Range('shipping_manufacturing', 'C38:N38').value = [(
    sum(df[(df['region'] == 'DS') &
           (df['product'] == 'ROJ')]['predicted_demand']) /
    sum(df[(df['region'] == 'DS') &
           ((df['product'] == 'FCOJ') |
            (df['product'] == 'ROJ'))]['predicted_demand'])) * 100] * 12

# S51
Range('shipping_manufacturing', 'C39:N39').value = [(
    sum(df[((df['region'] == 'NE') |
            (df['region'] == 'MA') |
            (df['region'] == 'SE')) &
           (df['product'] == 'ROJ')]['predicted_demand']) /
    sum(df[((df['region'] == 'NE') |
            (df['region'] == 'MA') |
            (df['region'] == 'SE')) &
           ((df['product'] == 'FCOJ') |
            (df['product'] == 'ROJ'))]['predicted_demand'])) * 100] * 12

# S59
Range('shipping_manufacturing', 'C40:N40').value = [(
    sum(df[((df['region'] == 'NW') |
            (df['region'] == 'SW')) &
           (df['product'] == 'ROJ')]['predicted_demand']) /
    sum(df[((df['region'] == 'NW') |
            (df['region'] == 'SW')) &
           ((df['product'] == 'FCOJ') |
            (df['product'] == 'ROJ'))]['predicted_demand'])) * 100] * 12

# S73
Range('shipping_manufacturing', 'C41:N41').value = [(
    sum(df[(df['region'] == 'MW') &
           (df['product'] == 'ROJ')]['predicted_demand']) /
    sum(df[(df['region'] == 'MW') &
           ((df['product'] == 'FCOJ') |
            (df['product'] == 'ROJ'))]['predicted_demand'])) * 100] * 12


### Pricing
# ORA
Range('pricing', 'D6:O6').value = [float(
    df[(df['region'] == 'NE') &
       (df['product'] == 'ORA')]['price'])] * 12
Range('pricing', 'D7:O7').value = [float(
    df[(df['region'] == 'MA') &
       (df['product'] == 'ORA')]['price'])] * 12
Range('pricing', 'D8:O8').value = [float(
    df[(df['region'] == 'SE') &
       (df['product'] == 'ORA')]['price'])] * 12
Range('pricing', 'D9:O9').value = [float(
    df[(df['region'] == 'MW') &
       (df['product'] == 'ORA')]['price'])] * 12
Range('pricing', 'D10:O10').value = [float(
    df[(df['region'] == 'DS') &
       (df['product'] == 'ORA')]['price'])] * 12
Range('pricing', 'D11:O11').value = [float(
    df[(df['region'] == 'NW') &
       (df['product'] == 'ORA')]['price'])] * 12
Range('pricing', 'D12:O12').value = [float(
    df[(df['region'] == 'SW') &
       (df['product'] == 'ORA')]['price'])] * 12

# POJ
Range('pricing', 'D15:O15').value = [float(
    df[(df['region'] == 'NE') &
       (df['product'] == 'POJ')]['price'])] * 12
Range('pricing', 'D16:O16').value = [float(
    df[(df['region'] == 'MA') &
       (df['product'] == 'POJ')]['price'])] * 12
Range('pricing', 'D17:O17').value = [float(
    df[(df['region'] == 'SE') &
       (df['product'] == 'POJ')]['price'])] * 12
Range('pricing', 'D18:O18').value = [float(
    df[(df['region'] == 'MW') &
       (df['product'] == 'POJ')]['price'])] * 12
Range('pricing', 'D19:O19').value = [float(
    df[(df['region'] == 'DS') &
       (df['product'] == 'POJ')]['price'])] * 12
Range('pricing', 'D20:O20').value = [float(
    df[(df['region'] == 'NW') &
       (df['product'] == 'POJ')]['price'])] * 12
Range('pricing', 'D21:O21').value = [float(
    df[(df['region'] == 'SW') &
       (df['product'] == 'POJ')]['price'])] * 12

# ROJ
Range('pricing', 'D24:O24').value = [float(
    df[(df['region'] == 'NE') &
       (df['product'] == 'ROJ')]['price'])] * 12
Range('pricing', 'D25:O25').value = [float(
    df[(df['region'] == 'MA') &
       (df['product'] == 'ROJ')]['price'])] * 12
Range('pricing', 'D26:O26').value = [float(
    df[(df['region'] == 'SE') &
       (df['product'] == 'ROJ')]['price'])] * 12
Range('pricing', 'D27:O27').value = [float(
    df[(df['region'] == 'MW') &
       (df['product'] == 'ROJ')]['price'])] * 12
Range('pricing', 'D28:O28').value = [float(
    df[(df['region'] == 'DS') &
       (df['product'] == 'ROJ')]['price'])] * 12
Range('pricing', 'D29:O29').value = [float(
    df[(df['region'] == 'NW') &
       (df['product'] == 'ROJ')]['price'])] * 12
Range('pricing', 'D30:O30').value = [float(
    df[(df['region'] == 'SW') &
       (df['product'] == 'ROJ')]['price'])] * 12

# FCOJ
Range('pricing', 'D33:O33').value = [float(
    df[(df['region'] == 'NE') &
       (df['product'] == 'FCOJ')]['price'])] * 12
Range('pricing', 'D34:O34').value = [float(
    df[(df['region'] == 'MA') &
       (df['product'] == 'FCOJ')]['price'])] * 12
Range('pricing', 'D35:O35').value = [float(
    df[(df['region'] == 'SE') &
       (df['product'] == 'FCOJ')]['price'])] * 12
Range('pricing', 'D36:O36').value = [float(
    df[(df['region'] == 'MW') &
       (df['product'] == 'FCOJ')]['price'])] * 12
Range('pricing', 'D37:O37').value = [float(
    df[(df['region'] == 'DS') &
       (df['product'] == 'FCOJ')]['price'])] * 12
Range('pricing', 'D38:O38').value = [float(
    df[(df['region'] == 'NW') &
       (df['product'] == 'FCOJ')]['price'])] * 12
Range('pricing', 'D39:O39').value = [float(
    df[(df['region'] == 'SW') &
       (df['product'] == 'FCOJ')]['price'])] * 12

# Need to save and close!!