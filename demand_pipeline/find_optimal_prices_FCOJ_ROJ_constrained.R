library(dplyr)
library(ggplot2)

all.demands <- read.csv('all_predicted_demands.csv',
    stringsAsFactors=FALSE)
fcoj.df <- all.demands[all.demands$product == 'FCOJ', ]
roj.demands <- all.demands[all.demands$product == 'ROJ', ]

FCOJ.FUTURE.PRICE <- 0.961788527

fcoj.df$weekly_revenue <- fcoj.df$price *
    fcoj.df$predicted_demand * 2000
fla.to.s35 <- 1522
fla.to.s51 <- 967
fla.to.s59 <- 2961
fla.to.s73 <- 1470
fcoj.df$fla.to.storage <- c(rep(fla.to.s51, 903),
                                 rep(fla.to.s73, 301),
                                 rep(fla.to.s35, 301),
                                 rep(fla.to.s59, 602))
fcoj.df$fla.to.storage.cost <- 0.22 *
    fcoj.df$predicted_demand *
    fcoj.df$fla.to.storage
fcoj.df$storage.to.market <- c(rep(479.1429, 301),
                                    rep(286.7647, 301),
                                    rep(712.1667, 301),
                                    rep(368.5909, 301),
                                    rep(413.3750, 301),
                                    rep(659.1250, 301),
                                    rep(659, 301))
fcoj.df$storage.to.market.cost <- 1.2 *
    fcoj.df$predicted_demand *
    fcoj.df$storage.to.market

fcoj.df$purchase_cost <- fcoj.df$predicted_demand * 2000 * FCOJ.FUTURE.PRICE

fcoj.df$profit <- fcoj.df$weekly_revenue - (
    fcoj.df$fla.to.storage.cost +
    fcoj.df$storage.to.market.cost +
    fcoj.df$purchase_cost)

roj.df <- roj.demands %>%
    mutate(weekly_revenue=2000 * price * predicted_demand,
           weekly_demand = predicted_demand)

roj.df$fla.to.storage <- c(rep(fla.to.s51, 903),
                                 rep(fla.to.s73, 301),
                                 rep(fla.to.s35, 301),
                                 rep(fla.to.s59, 602))
roj.df$fla.to.storage.cost <- 0.22 *
    roj.df$weekly_demand *
    roj.df$fla.to.storage

# Add storage to market distances
roj.df$storage.to.market <- c(rep(479.1429, 301),
                         rep(286.7647, 301),
                         rep(712.1667, 301),
                         rep(368.5909, 301),
                         rep(413.3750, 301),
                         rep(659.1250, 301),
                         rep(659, 301))
roj.df$storage.to.market.cost <- 1.2 *
    roj.df$weekly_demand *
    roj.df$storage.to.market

roj.df$purchase_cost <- roj.df$weekly_demand * 2000 * FCOJ.FUTURE.PRICE
roj.df$reconstitution_cost <- roj.df$weekly_demand * 650

roj.df$profit <- roj.df$weekly_revenue - (
    roj.df$fla.to.storage.cost +
    roj.df$storage.to.market.cost +
    roj.df$purchase_cost +
    roj.df$reconstitution_cost)

# rewritten above for smart indexing
get.profits <- function(region.fcoj.prices,
                        region.roj.prices) {
    # order in both FCOJ and ROJ dfs is
    # NE, MA, SE, MW, DS, NW, SW
    ind1 <- (region.fcoj.prices[1] - 1) / 0.01 + 1
    ind2 <- (region.fcoj.prices[2] - 1) / 0.01 + 302
    ind3 <- (region.fcoj.prices[3] - 1) / 0.01 + 603
    ind4 <- (region.fcoj.prices[4] - 1) / 0.01 + 904
    ind5 <- (region.fcoj.prices[5] - 1) / 0.01 + 1205
    ind6 <- (region.fcoj.prices[6] - 1) / 0.01 + 1506
    ind7 <- (region.fcoj.prices[7] - 1) / 0.01 + 1807
    fcoj <- fcoj.df[c(ind1, ind2, ind3, ind4, ind5, ind6, ind7),
                         c(1, 3, 4, 5, ncol(fcoj.df))]
    ind1 <- (region.roj.prices[1] - 1) / 0.01 + 1
    ind2 <- (region.roj.prices[2] - 1) / 0.01 + 302
    ind3 <- (region.roj.prices[3] - 1) / 0.01 + 603
    ind4 <- (region.roj.prices[4] - 1) / 0.01 + 904
    ind5 <- (region.roj.prices[5] - 1) / 0.01 + 1205
    ind6 <- (region.roj.prices[6] - 1) / 0.01 + 1506
    ind7 <- (region.roj.prices[7] - 1) / 0.01 + 1807                
    roj <- roj.df[c(ind1, ind2, ind3, ind4, ind5, ind6, ind7),
                  c(1, 3, 4, 5, ncol(roj.df))]

    return(rbind(fcoj, roj))
}

get.obj.const <- function(fcoj.prices, roj.prices) {
    df <- get.profits(fcoj.prices, roj.prices)
    return(c(sum(df$profit),
             sum(df$predicted_demand)))
}

# We run some number of iterations, sampling random prices
ITER <- 100000
profits <- rep(NA, ITER)

# This constraint depends on our quantity of maturing contracts
# (which through 2020 is 136k) and the number of weeks we
# can have them arrive through.  Usually this is 48, but for
# years where we need to clear out in the first month and avoid
# inventory problems, we set it to 44.
QUANTITY <- 136000
CONSTRAINT <- QUANTITY / 48
fcoj.prices.mat <- matrix(NA, ITER, 7)
roj.prices.mat <- matrix(NA, ITER, 7)

for (i in 1:ITER) {
    # Lower end of prices at 1.5 because we know those have
    # negative profit, and to improve our chances of getting
    # good samplings.
    fcoj.prices <- round(runif(7, 1.5, 4), 2)
    roj.prices <- round(runif(7, 2, 4), 2)
    results <- get.obj.const(fcoj.prices, roj.prices)
    if (results[2] < CONSTRAINT) {
        profits[i] <- results[1]
        fcoj.prices.mat[i, ] <- fcoj.prices
        roj.prices.mat[i, ] <- roj.prices
    }
}

max.ind <- which.max(profits)
fcoj.prices <- fcoj.prices.mat[max.ind, ]
roj.prices <- roj.prices.mat[max.ind, ]
regions <- unique(fcoj.df$region)
constrained <- data.frame(
    matrix(NA, 2 * length(fcoj.prices), 6))
colnames(constrained) <- colnames(fcoj.df)[c(1:5, 11)]
for (i in 1:length(fcoj.prices)) {
    constrained[i, ] <- fcoj.df[
        fcoj.df$region == regions[i] &
        fcoj.df$price == fcoj.prices[i], c(1:5, 11)]
}
for (i in 1:length(roj.prices)) {
    constrained[i + 7, ] <- roj.df[
        roj.df$region == regions[i] &
        roj.df$price == roj.prices[i], c(1:5, 13)]
}

write.csv(constrained,
          'profit_csvs/fcoj_and_roj_fixed_quantity.csv',
          quote=FALSE, row.names=FALSE)


unconstrained <- rbind(read.csv(
    'profit_csvs/fcoj_futures_max_profit.csv')[,c(1:5, 12)],
                 read.csv(
    'profit_csvs/roj_futures_max_profit.csv')[,c(1:5, 13)])
