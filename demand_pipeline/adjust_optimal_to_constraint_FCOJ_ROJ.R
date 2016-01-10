args <- commandArgs(trailingOnly = TRUE)
FCOJ.FUTURE.PRICE <- as.numeric(args[1])
FCOJ.FUTURES.MATURING <- as.integer(args[2])

fcoj <- read.csv('profit_csvs/fcoj_futures_max_profit.csv')
roj <- read.csv('profit_csvs/roj_futures_max_profit.csv')
# ^ optimal

all.predicted.demands <- read.csv(
    'all_predicted_demands.csv',
    stringsAsFactors=FALSE)
fcoj.df <- all.predicted.demands[
    all.predicted.demands$product == 'FCOJ', ]

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

roj.df <- all.predicted.demands[
    all.predicted.demands$product == 'ROJ', ]
roj.df$weekly_revenue <- roj.df$price *
    roj.df$predicted_demand * 2000

roj.df$fla.to.storage <- c(rep(fla.to.s51, 903),
                                 rep(fla.to.s73, 301),
                                 rep(fla.to.s35, 301),
                                 rep(fla.to.s59, 602))
roj.df$fla.to.storage.cost <- 0.22 *
    roj.df$predicted_demand *
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
    roj.df$predicted_demand *
    roj.df$storage.to.market

roj.df$purchase_cost <- roj.df$predicted_demand * 2000 * FCOJ.FUTURE.PRICE
roj.df$reconstitution_cost <- roj.df$predicted_demand * 650

roj.df$profit <- roj.df$weekly_revenue - (
    roj.df$fla.to.storage.cost +
    roj.df$storage.to.market.cost +
    roj.df$purchase_cost +
    roj.df$reconstitution_cost)


initial.annual.profit <- (sum(fcoj$profit) +
                          sum(roj$profit)) * 48
initial.annual.demand <- (sum(fcoj$predicted_demand) +
                          sum(roj$predicted_demand)) * 48
print('Starting annual profit:')
print(initial.annual.profit)
print('Starting annual demand:')
print(initial.annual.demand)

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

if (initial.annual.demand < FCOJ.FUTURES.MATURING) {
    annual.demand <- initial.annual.demand
    while (FCOJ.FUTURES.MATURING - annual.demand > 50) {
        fcoj$price <- fcoj$price - 0.01
        roj$price <- roj$price - 0.01
        tmp <- get.profits(fcoj$price, roj$price)
        annual.demand <- sum(tmp$predicted_demand) * 48
    }
} else if (initial.annual.demand > FCOJ.FUTURES.MATURING) {
    annual.demand <- initial.annual.demand
    while (annual.demand - FCOJ.FUTURES.MATURING > 50) {
        fcoj$price <- fcoj$price + 0.01
        roj$price <- roj$price + 0.01
        tmp <- get.profits(fcoj$price, roj$price)
        annual.demand <- sum(tmp$predicted_demand) * 48
    }
}

print('Adjusted annual profit:')
print(sum(tmp$profit) * 48)
print('Adjusted annual demand:')
print(annual.demand)

write.csv(fcoj,
          file='profit_csvs/fcoj_futures_max_profit_adj.csv',
          quote=FALSE, row.names=FALSE)
write.csv(roj,
          file='profit_csvs/roj_futures_max_profit_adj.csv',
          quote=FALSE, row.names=FALSE)