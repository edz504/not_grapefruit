# What if we converted all incoming FCOJ futures to ROJ?
library(dplyr)
library(ggplot2)

cwd <- getwd()
setwd('..')
all.demands <- read.csv('fit_demand/all_predicted_demands.csv',
    stringsAsFactors=FALSE)
roj.demands <- all.demands[all.demands$product == 'ROJ', ]

roj.demands$weekly_revenue <- roj.demands$price *
    roj.demands$predicted_demand * 2000
fla.to.s35 <- 1522
fla.to.s51 <- 967
fla.to.s59 <- 2961
fla.to.s73 <- 1470
roj.demands$fla.to.storage <- c(rep(fla.to.s51, 903),
                                 rep(fla.to.s73, 301),
                                 rep(fla.to.s35, 301),
                                 rep(fla.to.s59, 602))
roj.demands$fla.to.storage.cost <- 0.22 *
    roj.demands$predicted_demand *
    roj.demands$fla.to.storage
closest.storage.dists <- read.csv(
    'fit_demand/region_storage_dists_opt.csv')
roj.demands$storage.to.market <- c(rep(479.1429, 301),
                                    rep(286.7647, 301),
                                    rep(712.1667, 301),
                                    rep(368.5909, 301),
                                    rep(413.3750, 301),
                                    rep(659.1250, 301),
                                    rep(659, 301))
roj.demands$storage.to.market.cost <- 1.2 *
    roj.demands$predicted_demand *
    roj.demands$storage.to.market

roj.demands$reconstitution.cost <- 650 *
    roj.demands$predicted_demand

roj.demands$profit <- roj.demands$weekly_revenue - (
    roj.demands$fla.to.storage.cost +
    roj.demands$storage.to.market.cost +
    roj.demands$reconstitution.cost)

opt <- roj.demands %>%
    group_by(region) %>%
        filter(profit==max(profit)) %>%
            select(region, price,
                   predicted_demand, weekly_revenue,
                   profit)

print('Profit - purchase cost')
sum(opt$profit) - (1.12847 * 136000 * 2000 / 48)
# We would lose $559,030.70 / week, even at the profit-maximizing
# price (given FCOJ futures).