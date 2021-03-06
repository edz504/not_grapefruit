### Command-line argument is the latest year to update for.
import numpy as np
import pandas as pd
import os
import sys
from utilities import get_spot_purchase_values

year = int(sys.argv[1])

all_raw_price_df = pd.read_csv('all_raw_price_df.csv')
all_exchange_rate_df = pd.read_csv('all_exchange_rate_df.csv')
all_quantity_df = pd.read_csv('all_quantity_df.csv')

if float(year) not in list(all_raw_price_df['year']):
    raw_price_df, exchange_rate_df, quantity_df = get_spot_purchase_values(year)
    raw_price_leveled = raw_price_df.unstack().reorder_levels(
        [1, 0]).reset_index()
    raw_price_leveled.columns = ['grove', 'month', 'price']
    raw_price_leveled['year'] = year
    all_raw_price_df = pd.concat((all_raw_price_df, raw_price_leveled))
    exchange_rate_leveled = exchange_rate_df.unstack().reorder_levels(
        [1, 0]).reset_index()
    exchange_rate_leveled.columns = ['foreign', 'month', 'rate']
    exchange_rate_leveled['year'] = year
    all_exchange_rate_df = pd.concat((all_exchange_rate_df,
                                      exchange_rate_leveled))
    quantity_leveled = quantity_df.unstack().reorder_levels(
        [1, 0]).reset_index()
    quantity_leveled.columns = ['grove', 'month', 'quantity']
    quantity_leveled['year'] = year
    all_quantity_df = pd.concat((all_quantity_df,
                                 quantity_leveled))

    raw_price_beliefs_mean = all_raw_price_df.groupby(
        ['grove', 'month'])['price'].mean().reorder_levels(
        [1, 0]).reset_index()
    raw_price_beliefs_std = all_raw_price_df.groupby(
        ['grove', 'month'])['price'].std().reorder_levels(
        [1, 0]).reset_index()

    exchange_rate_beliefs_mean = all_exchange_rate_df.groupby(
        ['foreign', 'month'])['rate'].mean().reorder_levels(
        [1, 0]).reset_index()
    exchange_rate_beliefs_std = all_exchange_rate_df.groupby(
        ['foreign', 'month'])['rate'].std().reorder_levels(
        [1, 0]).reset_index()

    quantity_beliefs_mean = all_quantity_df.groupby(
        ['grove', 'month'])['quantity'].mean().reorder_levels(
        [1, 0]).reset_index()
    quantity_beliefs_std = all_quantity_df.groupby(
        ['grove', 'month'])['quantity'].std().reorder_levels(
        [1, 0]).reset_index()

    all_raw_price_df.to_csv('all_raw_price_df.csv',
        index=False)
    all_exchange_rate_df.to_csv('all_exchange_rate_df.csv',
        index=False)
    all_quantity_df.to_csv('all_quantity_df.csv',
        index=False)

    raw_price_beliefs_mean.to_csv('raw_price_beliefs_mean.csv',
        index=False)
    raw_price_beliefs_std.to_csv('raw_price_beliefs_std.csv',
        index=False)
    exchange_rate_beliefs_mean.to_csv('exchange_rate_beliefs_mean.csv',
        index=False)
    exchange_rate_beliefs_std.to_csv('exchange_rate_beliefs_std.csv',
        index=False)
    quantity_beliefs_mean.to_csv('quantity_beliefs_mean.csv',
        index=False)
    quantity_beliefs_std.to_csv('quantity_beliefs_std.csv',
        index=False)
else:
    print '{0} data already in grove beliefs'.format(year)