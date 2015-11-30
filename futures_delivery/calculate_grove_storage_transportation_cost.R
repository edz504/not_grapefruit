setwd('..')
fcoj.demands.at.profit.max <- read.csv(
    'clean_demand/fcoj_max_profit_opt.csv')

s35.weekly.demand <- fcoj.demands.at.profit.max$weekly_demand[5]
s51.weekly.demand <- sum(
    fcoj.demands.at.profit.max$weekly_demand[c(1, 2, 3)])
s59.weekly.demand <- sum(
    fcoj.demands.at.profit.max$weekly_demand[c(6, 7)])
s73.weekly.demand <- fcoj.demands.at.profit.max$weekly_demand[4]

fla.to.s35 <- 1522
fla.to.s51 <- 967
fla.to.s59 <- 2961
fla.to.s73 <- 1470

print('Weekly grove->storage cost: ')
0.22 * (s35.weekly.demand * fla.to.s35 +
        s51.weekly.demand * fla.to.s51 +
        s59.weekly.demand * fla.to.s59 +
        s73.weekly.demand * fla.to.s73)
print('Weekly revenue: ')
sum(fcoj.demands.at.profit.max$price *
    fcoj.demands.at.profit.max$weekly_demand * 2000)

# read in the average distance to closest storage for each region
closest.storage.dists <- read.csv(
    'clean_demand/region_storage_dists_opt.csv')
print('Weekly storage->market cost: ')
1.2 * (s35.weekly.demand * closest.storage.dists$d[1] +
       s51.weekly.demand * sum(closest.storage.dists$d[c(2, 4, 6)]) +
       s59.weekly.demand * sum(closest.storage.dists$d[c(5, 7)]) +
       s73.weekly.demand * sum(closest.storage.dists$d[3]))

print ('Annual grove->storage cost: ')
0.22 * (s35.weekly.demand * fla.to.s35 +
        s51.weekly.demand * fla.to.s51 +
        s59.weekly.demand * fla.to.s59 +
        s73.weekly.demand * fla.to.s73) * 48
print ('Annual futures purchase cost: ')
1.12847 * 136000 * 2000
print('Annual storage->market cost: ')
1.2 * (s35.weekly.demand * closest.storage.dists$d[1] +
       s51.weekly.demand * sum(closest.storage.dists$d[c(2, 4, 6)]) +
       s59.weekly.demand * sum(closest.storage.dists$d[c(5, 7)]) +
       s73.weekly.demand * sum(closest.storage.dists$d[3])) * 48

print('Annual revenue: ')
sum(fcoj.demands.at.profit.max$price *
    fcoj.demands.at.profit.max$weekly_demand * 2000) * 48


# The above shows that we lose about $15m :(


############# disregard
# Let's see what happens
# if we use our fitted demand curve and look at various prices, using
# this singled out optimization instead of the calculation used to
# find "max-profit prices" earlier.
fitted.demands <- read.csv('fit_demand/demand_fit_coefs.csv',
    stringsAsFactors=FALSE)
fcoj.fitted.demands <- fitted.demands[fitted.demands$product == 'FCOJ',]

# Finding profit at various prices for S35 (DS only)
# Note that after finding the optimal price and totalling profit, we
# need to again subtract the futures purchase cost, which does not
# belong to any singular region.
p.vec <- seq(1, 4, by=0.01)
s35.profit <- rep(NA, length(p.vec))
i <- 1
for (p in p.vec) {
    demands <- fcoj.fitted.demands$c1 / p^2 + fcoj.fitted.demands$intercept
    s35.weekly.demand <- demands[5]
    grove.to.storage <- 0.22 * s35.weekly.demand * fla.to.s35 * 48
    storage.to.market <- 1.2 * s35.weekly.demand * closest.storage.dists$d[1] * 48
    rev <- 2000 * p * s35.weekly.demand * 48
    s35.profit[i] = rev - (grove.to.storage + storage.to.market)
    i <- i + 1
}
# The above actually only makes sense if we're creating FCOJ.
# But we're actually limited to 136k FCOJ, so we need to figure out
# how to distribute that
##############


# Quantitatively, based off of the fitted
# demand curves, MW (S73) has a high FCOJ demand, and
# SE + NE + MA (S51) also do, while NW + SW (S59) and DS (S35) aren't
# as high.

# If we send 2000 of the 2833 to S73 (MW) and price at $1, and
# send the remaining 833 to S51 (SE / NE / MA) and price at $1, how
# much profit do we make?
s73.revenue <- 1 * 2000 * 2000 * 48
fla.to.s73.cost <- 0.22 * 2000 * fla.to.s73 * 48
s73.to.market.cost <- 1.2 * 2000 * closest.storage.dists$d[3] * 48

se.ne.ma <- c(1500, 1500, 1250)
s51.proportions <- se.ne.ma / sum(se.ne.ma)
s51.revenue <- 1 * 2000 * 833 * 48
fla.to.s51.cost <- 0.22 * 833 * fla.to.s51 * 48
s51.to.market.cost <- 1.2 * ((s51.proportions[1] * 833) * closest.storage.dists$d[6] +
                             (s51.proportions[2] * 833) * closest.storage.dists$d[4] +
                             (s51.proportions[3] * 833) * closest.storage.dists$d[2])

profit <- s73.revenue - (fla.to.s73.cost + s73.to.market.cost) +
          s51.revenue - (fla.to.s51.cost + s51.to.market.cost) -
          (1.12847 * 136000 * 2000)
# This loses us even more (-$117m)