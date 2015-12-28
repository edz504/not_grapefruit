This folder contains the code for updating the demand curves and making decisions.


1.
It uses VBA to create a csv from all past data (MomPop, Practice Rounds, and real rounds) with realized sales for a given price, product, and region.  It also provides a boolean indicating whether or not the sales represent censored demand (0 means clean).


2.
After the VBA script has been run, we fit demand curves.  We consider all data, but use a local / neighborhood max-based filtering method to filter out possibly censored data.  We use the following model structure for each curve:

D(p) = a / (p ^ 2) + b


3.
We then use the curves to discretize each demand curve with price-intervals of 1 cent.  This creates a lookup table where we input a price and obtain a weekly demand as output for a given price / region.


4.
Next, we run our profit-maximization script to obtain preliminary decisions.  For years 2016 through 2020, we have 136,000 FCOJ futures maturing.  In these years, we choose to sell all FCOJ futures as FCOJ, and satisfy ROJ demand through FCOJ manufacturing and subsequent reconstitution.  Therefore, we have two separate optimizations for these years -- the first finds the optimal prices for ORA, POJ, and ROJ (through manufacturing and reconstitution) given our demand beliefs, with no constraints.  The second optimization is done for FCOJ futures, given our maturing supply of futures (136k), it pseudo-optimizes through a random sampling to find a set of best-prices to set.

For the years from 2021 onwards, the quantity of maturing futures will be the 5-year-previous optimal quantity, which is likely less than 136k (e.g. 89k, 89k, 107k).  At 2021, we will cease manufacturing FCOJ and use the incoming futures to satisfy both FCOJ demand and reconstituting to satisfy ROJ demand.  This means that our first optimization only needs to take care of ORA and POJ -- the second optimization then does the same process for ROJ and FCOJ, but without a fixed quantity of supply.

For example, the optimization might tell us that the profit-maximizing price gives a demanded supply of X FCOJ futures over the whole year.  The trick here is that we're removing the supply constraint under the assumption that the figure we came up with 5 years previous is close enough to the optimal number here that we will have enough.  For example, we're assuming that 5 years ago, the optimal number we came up with using the ROJ/FCOJ script (non-constrained), is approximately (or, in a worse case, more than) the amount X that our current beliefs tell us is optimal.

Note that pre-2021, we still need to run the find_optimal_prices_ROJ_FCOJ.R script in order to obtain our 5 year ahead beliefs for the optimal quantity to order.


5.


======
Pipeline
1.  John's VBA or, hopefully, rewritten Python
2.  demand_fit_plot.R
3.  create_demand_table.R
4.  find_optimal_prices_ORA_POJ_ROJ.R,   ** non-constrained
    find_optimal_prices_FCOJ_fixed.R     ** constrained
    find_optimal_prices_ROJ_FCOJ.R       ** non-constrained
