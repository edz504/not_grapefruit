suppressMessages(library(ggplot2))
suppressMessages(library(dplyr))

all.demands <- read.csv('all_predicted_demands.csv',
    stringsAsFactors=FALSE)
fcoj.demands <- all.demands[all.demands$product == 'FCOJ', ]

args <- commandArgs(trailingOnly = TRUE)
ITER <- as.integer(args[1])
NUM_FUTURES <- as.integer(args[2])
WEEKS <- as.integer(args[3])
FCOJ.FUTURE.PRICE <- as.numeric(args[4])

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

fcoj.demands$purchase_cost <- fcoj.demands$predicted_demand * 2000 * FCOJ.FUTURE.PRICE

fcoj.demands$profit <- fcoj.demands$weekly_revenue - (
    fcoj.demands$fla.to.storage.cost +
    fcoj.demands$storage.to.market.cost +
    fcoj.demands$purchase_cost)

# opt <- fcoj.demands %>%
#     group_by(region) %>%
#         filter(profit==max(profit)) %>%
#             select(region, price,
#                    predicted_demand, weekly_revenue,
#                    profit)

# print('Profit - purchase cost')
# sum(opt$profit) - (1.12847 * 136000 * 2000 / 48)

# The above needs to be constrained by our supply, which
# need to sum to less than 2834, the weekly incoming supply.

# This function takes in a vector of prices
# (NE, MA, SE, MW, DS, NW, SW) and returns a dataframe
# with the relevant revenue and profit.
get.profits <- function(region.prices) {
    # ind1 <- which(fcoj.demands$region == 'NE' &
    #               fcoj.demands$price == region.prices[1])
    # ind2 <- which(fcoj.demands$region == 'MA' &
    #               fcoj.demands$price == region.prices[2])
    # ind3 <- which(fcoj.demands$region == 'SE' &
    #               fcoj.demands$price == region.prices[3])
    # ind4 <- which(fcoj.demands$region == 'MW' &
    #               fcoj.demands$price == region.prices[4])
    # ind5 <- which(fcoj.demands$region == 'DS' &
    #               fcoj.demands$price == region.prices[5])
    # ind6 <- which(fcoj.demands$region == 'NW' &
    #               fcoj.demands$price == region.prices[6])
    # ind7 <- which(fcoj.demands$region == 'SW' &
    #               fcoj.demands$price == region.prices[7])
    ind1 <- (region.prices[1] - 1) / 0.01 + 1
    ind2 <- (region.prices[2] - 1) / 0.01 + 302
    ind3 <- (region.prices[3] - 1) / 0.01 + 603
    ind4 <- (region.prices[4] - 1) / 0.01 + 904
    ind5 <- (region.prices[5] - 1) / 0.01 + 1205
    ind6 <- (region.prices[6] - 1) / 0.01 + 1506
    ind7 <- (region.prices[7] - 1) / 0.01 + 1807
    return(fcoj.demands[c(ind1, ind2, ind3, ind4, ind5, ind6, ind7),
                        c(1, 3, 4, 5, ncol(fcoj.demands))])
}

# f <- function(region.prices) {
#     df <- get.profits(region.prices)
#     return(sum(df$profit))
# }
# g <- function(region.prices) {
#     df <- get.profits(region.prices)
#     return(sum(df$predicted_demand))
# }

get.obj.const <- function(region.prices) {
    df <- get.profits(region.prices)
    return(c(sum(df$profit),
             sum(df$predicted_demand)))
}

# We run 500,000 iterations, sampling random prices
profits <- rep(NA, ITER)

# This constraint depends on our quantity of maturing contracts
# (which through 2020 is 136k) and the number of weeks we
# can have them arrive through.  Usually this is 48, but for
# years where we need to clear out in the first month and avoid
# inventory problems, we set it to 44.
CONSTRAINT <- NUM_FUTURES / WEEKS
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