library(dplyr)
library(ggplot2)

all.demands <- read.csv('all_predicted_demands.csv',
    stringsAsFactors=FALSE)
fcoj.demands <- all.demands[all.demands$product == 'FCOJ', ]
roj.demands <- all.demands[all.demands$product == 'ROJ', ]

fcoj.demands$weekly_revenue <- fcoj.demands$price *
    fcoj.demands$predicted_demand * 2000
fla.to.s35 <- 1522
fla.to.s51 <- 967
fla.to.s59 <- 2961
fla.to.s73 <- 1470
fcoj.demands$fla.to.storage <- c(rep(fla.to.s51, 903),
                                 rep(fla.to.s73, 301),
                                 rep(fla.to.s35, 301),
                                 rep(fla.to.s59, 602))
fcoj.demands$fla.to.storage.cost <- 0.22 *
    fcoj.demands$predicted_demand *
    fcoj.demands$fla.to.storage
fcoj.demands$storage.to.market <- c(rep(479.1429, 301),
                                    rep(286.7647, 301),
                                    rep(712.1667, 301),
                                    rep(368.5909, 301),
                                    rep(413.3750, 301),
                                    rep(659.1250, 301),
                                    rep(659, 301))
fcoj.demands$storage.to.market.cost <- 1.2 *
    fcoj.demands$predicted_demand *
    fcoj.demands$storage.to.market

fcoj.demands$profit <- fcoj.demands$weekly_revenue - (
    fcoj.demands$fla.to.storage.cost +
    fcoj.demands$storage.to.market.cost)

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

roj.df$weekly_storage_build <- 6000 * roj.df$weekly_demand / 48
roj.df$weekly_storage_maint <- (650 * roj.df$weekly_demand) / 48

roj.df$purchase_cost <- roj.df$weekly_demand * 2000 * 0.91
roj.df$reconstitution_cost <- roj.df$weekly_demand * 650

roj.df$year1_profit <- roj.df$weekly_revenue - (
    roj.df$fla.to.storage.cost +
    roj.df$storage.to.market.cost +
    roj.df$weekly_storage_build +
    roj.df$weekly_storage_maint +
    roj.df$purchase_cost +
    roj.df$reconstitution_cost)
roj.df$profit <- roj.df$year1_profit +
    roj.df$weekly_storage_build


# This function takes in a vector of prices
# (NE, MA, SE, MW, DS, NW, SW) and returns a dataframe
# with the relevant revenue and profit.
# get.profits <- function(region.prices) {
#     ind1 <- which(fcoj.demands$region == 'NE' &
#                   fcoj.demands$price == region.prices[1])
#     ind2 <- which(fcoj.demands$region == 'MA' &
#                   fcoj.demands$price == region.prices[2])
#     ind3 <- which(fcoj.demands$region == 'SE' &
#                   fcoj.demands$price == region.prices[3])
#     ind4 <- which(fcoj.demands$region == 'MW' &
#                   fcoj.demands$price == region.prices[4])
#     ind5 <- which(fcoj.demands$region == 'DS' &
#                   fcoj.demands$price == region.prices[5])
#     ind6 <- which(fcoj.demands$region == 'NW' &
#                   fcoj.demands$price == region.prices[6])
#     ind7 <- which(fcoj.demands$region == 'SW' &
#                   fcoj.demands$price == region.prices[7])
#     return(fcoj.demands[c(ind1, ind2, ind3, ind4, ind5, ind6, ind7),
#                         c(1, 3, 4, 5, ncol(fcoj.demands))])
# }

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
    fcoj <- fcoj.demands[c(ind1, ind2, ind3, ind4, ind5, ind6, ind7),
                         c(1, 3, 4, 5, ncol(fcoj.demands))]
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
regions <- unique(fcoj.demands$region)
optimal <- data.frame(
    matrix(NA, 2 * length(fcoj.prices), 6))
colnames(optimal) <- colnames(fcoj.demands)[c(1:5, 10)]
for (i in 1:length(fcoj.prices)) {
    optimal[i, ] <- fcoj.demands[
        fcoj.demands$region == regions[i] &
        fcoj.demands$price == fcoj.prices[i], c(1:5, 10)]
}
for (i in 1:length(roj.prices)) {
    optimal[i + 7, ] <- roj.df[
        roj.df$region == regions[i] &
        roj.df$price == roj.prices[i], c(1:5, 16)]
}

write.csv(optimal,
          'profit_csvs/fcoj_and_roj_fixed_quantity.csv',
          quote=FALSE, row.names=FALSE)


unconstrained <- rbind(read.csv(
    'profit_csvs/fcoj_futures_max_profit.csv')[,c(1:5, 15)],
                 read.csv(
    'profit_csvs/roj_futures_max_profit.csv')[,c(1:5, 16)])

optimal <- read.csv('profit_csvs/fcoj_and_roj_fixed_quantity.csv')