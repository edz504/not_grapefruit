library(dplyr)
library(ggplot2)

all.demands <- read.csv(
    'all_predicted_demands.csv',
    stringsAsFactors=FALSE)
fcoj.demands <- all.demands[all.demands$product == 'FCOJ', ]

fcoj.demands$weekly_revenue <- fcoj.demands$price *
    fcoj.demands$predicted_demand * 2000
fla.to.s21 <- 354
fla.to.s35 <- 1522
fla.to.s51 <- 967
fla.to.s59 <- 2961
fla.to.s73 <- 1470
fcoj.demands$fla.to.storage <- c(rep(fla.to.s51, 602),
                            rep(fla.to.s21, 301),
                            rep(fla.to.s73, 301),
                            rep(fla.to.s35, 301),
                            rep(fla.to.s59, 602))
fcoj.demands$fla.to.storage.cost <- 0.22 *
    fcoj.demands$predicted_demand *
    fcoj.demands$fla.to.storage
fcoj.demands$storage.to.market <- c(rep(479.1429, 301),
                               rep(286.7647, 301),
                               rep(290.5833, 301),
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

# The above needs to be constrained by our demands, which
# need to sum to less than 2834.

# This function takes in a vector of prices
# (NE, MA, SE, MW, DS, NW, SW) and returns a dataframe
# with the relevant revenue and profit.
get.profits <- function(region.prices) {
    ind1 <- which(fcoj.demands$region == 'NE' &
                  fcoj.demands$price == region.prices[1])
    ind2 <- which(fcoj.demands$region == 'MA' &
                  fcoj.demands$price == region.prices[2])
    ind3 <- which(fcoj.demands$region == 'SE' &
                  fcoj.demands$price == region.prices[3])
    ind4 <- which(fcoj.demands$region == 'MW' &
                  fcoj.demands$price == region.prices[4])
    ind5 <- which(fcoj.demands$region == 'DS' &
                  fcoj.demands$price == region.prices[5])
    ind6 <- which(fcoj.demands$region == 'NW' &
                  fcoj.demands$price == region.prices[6])
    ind7 <- which(fcoj.demands$region == 'SW' &
                  fcoj.demands$price == region.prices[7])
    return(fcoj.demands[c(ind1, ind2, ind3, ind4, ind5, ind6, ind7),
                        c(1, 3, 4, 5, ncol(fcoj.demands))])
}

f <- function(region.prices) {
    df <- get.profits(region.prices)
    return(sum(df$profit))
}
g <- function(region.prices) {
    df <- get.profits(region.prices)
    return(sum(df$predicted_demand))
}

get.obj.const <- function(region.prices) {
    df <- get.profits(region.prices)
    return(c(sum(df$profit),
             sum(df$predicted_demand)))
}

ITER <- 100000
profits <- rep(NA, ITER)
CONSTRAINT <- 136000 / 48
prices.mat <- matrix(NA, ITER, 7)
for (i in 1:ITER) {
  prices <- round(runif(7, 1, 4), 2)
  results <- get.obj.const(prices)
  if (results[2] < CONSTRAINT) {
    profits[i] <- results[1]
    prices.mat[i, ] <- prices
  }
}

prices <- prices.mat[which.max(profits), ]
regions <- unique(fcoj.demands$region)
optimal.fcoj <- data.frame(
    matrix(NA, length(prices), ncol(fcoj.demands)))
colnames(optimal.fcoj) <- colnames(fcoj.demands)

for (i in 1:length(prices)) {
    optimal.fcoj[i, ] <- fcoj.demands[
        fcoj.demands$region == regions[i] &
        fcoj.demands$price == prices[i],]
}

write.csv(optimal.fcoj, 'profit_csvs/fcoj_fixed_quantity.csv',
          quote=FALSE, row.names=FALSE)