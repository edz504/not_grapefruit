from xlwings import Workbook, Range
import numpy as np
import pandas as pd
import os

def get_spot_purchase_values(year):
    ROOT_DIR = os.path.dirname(os.getcwd())

    if year < 2005:
        raise ValueError('Data only goes back to 2005')
    elif year < 2015:
        wb = Workbook(os.path.join(
            ROOT_DIR, 'results/MomPop{0}.xlsm'.format(year)),
            app_visible=False)
    else:
        wb = Workbook(os.path.join(
            ROOT_DIR, 'results/notgrapefruit{0}.xlsm'.format(year)),
            app_visible=False)

    raw_price_df = pd.DataFrame(
        np.array(Range('grove', 'C5:N10', atleast_2d=True).value),
        columns=Range('grove', 'C4:N4').value,
        index=Range('grove', 'B5:B10').value)

    exchange_rate_df = pd.DataFrame(
        np.array(Range('grove', 'C14:N15', atleast_2d=True).value),
        columns=Range('grove', 'C13:N13').value,
        index=Range('grove', 'B14:B15').value)

    quantity_mat_weekly = np.array(
        Range('grove', 'C38:AX43', atleast_2d=True).value)
    # The matrix retrieved has values for each week.  We want an average weekly
    # quantity for the given month.
    quantity_mat_av = np.zeros((6, 12))
    for i in xrange(0, 12):
        this_month = quantity_mat_weekly[:, (4 * i):(4 * i + 4)]
        quantity_mat_av[:, i] = np.mean(this_month, 1)
    quantity_df = pd.DataFrame(quantity_mat_av,
                               index=Range('grove', 'B38:B43').value,
                               columns=Range('grove', 'C4:N4').value)
    wb.close()
    return (raw_price_df, exchange_rate_df, quantity_df)