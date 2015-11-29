from xlwings import Workbook, Range
import numpy as np
import pandas as pd
import os

def write_spot_purchase_prices(year):
    ROOT_DIR = os.path.dirname(os.getcwd())
    wb = Workbook(os.path.join(ROOT_DIR,
        'results/notgrapefruit{0}.xlsm'.format(year)))
    raw_price_df = pd.DataFrame(np.array(
        Range('grove', 'C5:N10', atleast_2d=True).value))
    raw_price_df.columns = Range('grove', 'C4:N4').value
    raw_price_df.index = Range('grove', 'B5:B10').value

    exchange_rate_df = pd.DataFrame(np.array(
        Range('grove', 'C14:N15', atleast_2d=True).value))
    exchange_rate_df.columns = Range('grove', 'C13:N13').value
    exchange_rate_df.index = Range('grove', 'B14:B15').value

    return (raw_price_df, exchange_rate_df)