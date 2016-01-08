This folder contains the code for updating the demand curves and making decisions.


1.
It uses a Python script to create a csv from all past data (MomPop, Practice Rounds, and real rounds) with realized sales for a given price, product, and region.  It also provides a boolean indicating whether or not the sales represent censored demand (0 means clean).


2.
After the Python script has been run, we re-fit demand curves.  We consider all data, but use a local / neighborhood max-based filtering method to filter out possibly censored data.  We use the following model structure for each curve:
    
D(p) = a / (p ^ 2) + b


3.
We then use the curves to discretize each demand curve with price-intervals of 1 cent.  This creates a lookup table where we input a price and obtain a weekly demand as output for a given price / region.


4.
Next, we run our profit-maximization script to obtain preliminary decisions.

We optimize ORA and POJ without constraints, and under the assumption that we use spot purchases to fill the profit-optimal demands.  We then optimize FCOJ and ROJ without constraints, and under the assumption ("Plan 2") that we use the maturing FCOJ contracts (purchased from 5 years ago) to fill FCOJ and ROJ demand -- without manufacturing any FCOJ.

The currently optimal FCOJ and ROJ amounts are obviously not going to align exactly with the optimal amount 5 years ago, so we perform a uniform adjustment to ensure that we use all of the FCOJ futures we actually have incoming.  The adjustment is simple: if the currently optimal demand is less than the incoming supply, we iteratively decrease all 14 (7 regions, 2 products) optimal prices by one cent.  Each iteration, we check if the newly increased demand is close enough to the incoming supply.  If we have more demand than supply, we again start at the optimal price points, and increase the prices uniformly until demand approximately matches supply.

Note that we also write the currently optimal FCOJ + ROJ demand into the 5-year maturity FCOJ futures purchase.

5.
Data wrangling, aggregation, and calculation to find the actual proportions and insert them into our decisions spreadsheet.

6.
Add beta price adjustments to our initial decisions spreadsheet.

7.
Run simulator and tune the prices.

8.
Update pricing adjustment beliefs.

======
Pipeline
1.  CollectSalesDataAcrossYears.py
    
    # Note, should modify to only add new year instead of going through all years each time.

    # Update: John has done this, I need to review it and add it.

2.  demand_fit_plot.R
3.  create_demand_table.R
4.  find_optimal_prices_ORA_POJ.R,
    find_optimal_prices_FCOJ_ROJ.R
    adjust_optimal_to_constraint_FCOJ_ROJ.R
    
5.  Copy blank decisions spreadsheet into folder, rename notgrapefruit20XX_init.xlsm
    calculate_and_write_decisions.py
6.  Copy notgrapefruit20XX_init.xlsm, rename notgrapefruit20XX.xlsm
    adjust_prices.py
7.  simulate.py (sanity check + fine tuning)
8.  update_pricing_adjustments.py