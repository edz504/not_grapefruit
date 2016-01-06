library(ggplot2)
library(dplyr)

all.predicted.demands <- read.csv(
    'all_predicted_demands.csv',
    stringsAsFactors=FALSE)

args <- commandArgs(trailingOnly = TRUE)
FCOJ.FUTURE.PRICE <- as.float(args[1])

# FCOJ
fcoj.df <- all.predicted.demands[
    all.predicted.demands$product == 'FCOJ',]
fcoj.df <- fcoj.df %>%
    mutate(revenue=2000 * price * predicted_demand,
           weekly_demand = predicted_demand)

# All futures ship from FLA
fla.to.s35 <- 1522
fla.to.s51 <- 967
fla.to.s59 <- 2961
fla.to.s73 <- 1470
fcoj.df$fla.to.storage <- c(rep(fla.to.s51, 903),
                                 rep(fla.to.s73, 301),
                                 rep(fla.to.s35, 301),
                                 rep(fla.to.s59, 602))
fcoj.df$fla.to.storage.cost <- 0.22 *
    fcoj.df$weekly_demand *
    fcoj.df$fla.to.storage

# Add storage to market distances
fcoj.df$storage.to.market <- c(rep(479.1429, 301),
                         rep(286.7647, 301),
                         rep(712.1667, 301),
                         rep(368.5909, 301),
                         rep(413.3750, 301),
                         rep(659.1250, 301),
                         rep(659, 301))
fcoj.df$storage.to.market.cost <- 1.2 *
    fcoj.df$weekly_demand *
    fcoj.df$storage.to.market

# fcoj.df$weekly_storage_build <- 6000 * fcoj.df$weekly_demand / 48
# fcoj.df$weekly_storage_maint <- (650 * fcoj.df$weekly_demand) / 48

fcoj.df$purchase_cost <- fcoj.df$weekly_demand * 2000 * FCOJ.FUTURE.PRICE

fcoj.df$profit <- fcoj.df$revenue - (
    fcoj.df$fla.to.storage.cost +
    fcoj.df$storage.to.market.cost +
    # fcoj.df$weekly_storage_build +
    # fcoj.df$weekly_storage_maint +
    fcoj.df$purchase_cost)
# fcoj.df$profit <- fcoj.df$year1_profit +
#     fcoj.df$weekly_storage_build
ggplot(fcoj.df, aes(x=price, y=profit, colour=region)) +
    geom_line(aes(y=profit)) +
    ggtitle('FCOJ Futures Profit')
ggsave('profit_curves/fcoj_futures_profit.png',
       width=10, height=6)

fcoj.profit.max <- fcoj.df %>% group_by(region) %>%
    filter(profit == max(profit))
write.csv(fcoj.profit.max,
          file='profit_csvs/fcoj_futures_max_profit.csv',
          quote=FALSE, row.names=FALSE)


# ROJ
roj.df <- all.predicted.demands[
    all.predicted.demands$product == 'ROJ',]
roj.df <- roj.df %>%
    mutate(revenue=2000 * price * predicted_demand,
           weekly_demand = predicted_demand)

# All futures ship from FLA
fla.to.s35 <- 1522
fla.to.s51 <- 967
fla.to.s59 <- 2961
fla.to.s73 <- 1470
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

# roj.df$weekly_storage_build <- 6000 * roj.df$weekly_demand / 48
# roj.df$weekly_storage_maint <- (650 * roj.df$weekly_demand) / 48

roj.df$purchase_cost <- roj.df$weekly_demand * 2000 * FCOJ.FUTURE.PRICE
roj.df$reconstitution_cost <- roj.df$weekly_demand * 650

roj.df$profit <- roj.df$revenue - (
    roj.df$fla.to.storage.cost +
    roj.df$storage.to.market.cost +
    # roj.df$weekly_storage_build +
    # roj.df$weekly_storage_maint +
    roj.df$purchase_cost +
    roj.df$reconstitution_cost)
# roj.df$profit <- roj.df$year1_profit +
#     roj.df$weekly_storage_build
ggplot(roj.df, aes(x=price, y=profit, colour=region)) +
    # geom_line(aes(y=year1_profit), linetype='dotted') +
    geom_line(aes(y=profit)) +
    ggtitle('ROJ Futures Profit')
ggsave('profit_curves/roj_futures_profit.png', width=10, height=6)

roj.profit.max <- roj.df %>% group_by(region) %>%
    filter(profit == max(profit))
write.csv(roj.profit.max,
          file='profit_csvs/roj_futures_max_profit.csv',
          quote=FALSE, row.names=FALSE)