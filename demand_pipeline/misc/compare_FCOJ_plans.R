# This script compares the profit-output in the lookahead model for the two
# futures plans, and gives us a suggestion for whether or not we should start
# Plan 2 now.


# Storage and processing maintenance costs, which are not included in profit csvs
# used in optimization.
proc <- 4 * 8e6 + 2500 * (250 + 750 + 250 + 250)
storage <- 4 * 7.5e6 + 650 * (1500 + 4000 + 1250 + 2000)

# Plan 1:
# ORA and POJ as usual, satisfy ROJ demand through manufacturing and
# reconstituting FCOJ.  Sell all 136k FCOJ futures as FCOJ.

ora <- read.csv('profit_csvs/ora_max_profit.csv')
poj <- read.csv('profit_csvs/poj_max_profit.csv')
roj <- read.csv('profit_csvs/roj_max_profit.csv')
fcoj <- read.csv('profit_csvs/fcoj_fixed_quantity.csv')

(sum(ora$profit) + sum(poj$profit) + sum(roj$profit) + sum(fcoj$profit)) * 48 -
(proc + storage)


# Plan 2:
# ORA and POJ as usual, split incoming 136k FCOJ futures into optimal quantities
# for ROJ and FCOJ.  We have 30k leftover FCOJ that we need to sell, though.
roj2 <- read.csv('profit_csvs/roj_futures_max_profit.csv')
fcoj2 <- read.csv('profit_csvs/fcoj_futures_max_profit.csv')

(sum(ora$profit) + sum(poj$profit) + sum(roj2$profit) + sum(fcoj2$profit)) * 48 -
(proc + storage)

# Plan 2 gives 50m more profit