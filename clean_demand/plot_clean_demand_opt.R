library(ggplot2)
library(dplyr)

# ORA
ora.df <- read.csv('ora_demand.csv')
ora.df <- ora.df %>%
    mutate(revenue=2000 * price * sales,
           month=ordered(month,
                         levels=c('Jan', 'Feb', 'Mar', 'Apr',
                         'May', 'Jun', 'Jul', 'Aug',
                         'Sep', 'Oct', 'Nov', 'Dec')),
           weekly_demand = demand / 4)

# We want to maximize profit, not revenue.
# Calculate transportation costs for each price + region.
# Each region has a mean distance for its markets to the closest
# storage.  Let's also assume that for grove to storage, we'll
# ship spot purchases from CAL to S59, TEX to S35, FLA to S51,
# FLA to S73.
s35.grove.dist <- 266
s51.grove.dist <- 967
s59.grove.dist <- 176
s73.grove.dist <- 1470

region.storage <- read.csv('region_storage_dists_opt.csv')
ora.df$storage_dist <- c(rep(479.1429, 12),
                         rep(286.7647, 12),
                         rep(712.1667, 12),
                         rep(368.5909, 12),
                         rep(413.3750, 12),
                         rep(659.1250, 12),
                         rep(659, 12))
ora.df$grove_dist <- c(rep(s51.grove.dist, 36),
                       rep(s73.grove.dist, 12),
                       rep(s35.grove.dist, 12),
                       rep(s59.grove.dist, 24))
ora.df$weekly_transp_cost <- ora.df$weekly_demand *
  (0.22 * ora.df$grove_dist + 1.2 * ora.df$storage_dist)

# Also include cost to buy capacity and maintain necessary
# storage. There's a one-time upgrade cost and an every-year
# maintenance. Divide the one-time cost by 48 to "week-ize" it.
ora.df$weekly_storage_build <- 6000 * ora.df$weekly_demand / 48
ora.df$weekly_storage_maint <- (4 * 7500000 + 650 * ora.df$weekly_demand) / 48

# Finally, include the raw material cost (spot purchase of ORA).
# We use our mean belief for each grove's spot purchase price.
# (FLA x 36, FLA x 12, TEX x 12, CAL x 24) is the vectoring.
# Average over months for now, disregarding seasonality -- also,
# no need to factor in exchange rates for now, assume we buy from
# FLA, not FLA / BRA / SPA.

cwd <- getwd()
setwd('..') # move up one directory
mean.raw.price.beliefs <- read.csv(
    'beliefs/raw_price_beliefs_mean.csv')
setwd(cwd)

mean.over.months <- mean.raw.price.beliefs %>%
    group_by(grove) %>%
    summarise(mean_month=mean(price))
ora.df$raw_material_cost <- ora.df$weekly_demand * 2000 * c(
    rep(mean.over.months[mean.over.months$grove == 'FLA', ]$mean_month,
        48),
    rep(mean.over.months[mean.over.months$grove == 'TEX', ]$mean_month,
        12),
    rep(mean.over.months[mean.over.months$grove == 'CAL', ]$mean_month,
        24))

# Note: this "profit" is for the first year, actual profit
# should be even higher in later years when we don't have the
# capacity cost.
ora.df$profit <- ora.df$revenue - (ora.df$weekly_transp_cost +
    ora.df$weekly_storage_build + ora.df$weekly_storage_maint +
    ora.df$raw_material_cost)
write.csv(ora.df, file='ora_demand_opt.csv',
          quote=FALSE, row.names=FALSE)
ggplot(ora.df, aes(x=price, y=profit, colour=region)) +
    geom_point() + geom_line() +
    ggtitle('ORA Profit (Revenue - Trans. Costs)')
ggsave('ora_clean_profit_opt.png', width=10, height=6)

ora.profit.max <- ora.df %>% group_by(region) %>%
    filter(profit == max(profit)) %>% select(-month)
write.csv(ora.profit.max, file='ora_max_profit_opt.csv',
          quote=FALSE, row.names=FALSE)


# POJ
poj.df <- read.csv('poj_demand.csv')
poj.df <- poj.df %>%
    mutate(revenue=2000 * price * demand,
           month=ordered(month,
                         levels=c('Jan', 'Feb', 'Mar', 'Apr',
                         'May', 'Jun', 'Jul', 'Aug',
                         'Sep', 'Oct', 'Nov', 'Dec')),
           weekly_demand = demand / 4)

# Add storage to market distances
poj.df$storage_dist <- c(rep(479.1429, 12),
                         rep(286.7647, 12),
                         rep(712.1667, 12),
                         rep(368.5909, 12),
                         rep(413.3750, 12),
                         rep(659.1250, 12),
                         rep(659, 12))

# Instead of grove to storage, now we have grove to plant and
# plant to storage distances.  We can make similar "efficiency"
# assumptions, where P2->S35, P3->S51, P5->S59, P9->S73.
# We'll ship raw ORA from TEX->P2, CAL->P5, FLA->P3, FLA->P9.

# TEX->P2 = 381
# CAL->P5 = 351
# FLA->P3 = 773
# FLA->P9 = 1528
poj.df$g_p_dist <- c(rep(773, 36),
                     rep(1528, 12),
                     rep(381, 12),
                     rep(351, 24))

# P2 -> S35 = 140
# P3 -> S51 = 317
# P5 -> S59 = 393
# P9 -> S73 = 98
poj.df$p_s_dist <- c(rep(317, 36),
                     rep(98, 12),
                     rep(140, 12),
                     rep(393, 24))
# For tanker car cost, we need to calculate how many tanker
# cars the given demand would require, multiply by its purchase
# cost, and then add the weekly traveling cost.  We'll spread the
# one time purchase cost over weeks by dividing it by 48.

poj.df$num_tanker_cars_needed <- poj.df$weekly_demand / 30
poj.df$tanker_car_weekly_purchase_cost <- 
    poj.df$num_tanker_cars_needed * 100000 / 48
poj.df$tanker_car_weekly_travel_cost <- 36 *
    poj.df$num_tanker_cars_needed * poj.df$p_s_dist

poj.df$g_p_weekly_cost <- 0.22 * poj.df$weekly_demand * poj.df$g_p_dist
poj.df$storage_market_weekly_cost <- 1.2 * poj.df$weekly_demand *
    poj.df$storage_dist

# Also include cost to buy capacity and maintain necessary
# processing. There's a one-time upgrade cost and an every-year
# maintenance. Divide the one-time cost by 48 to "week-ize" it.
poj.df$weekly_proc_build <- 8000 * poj.df$weekly_demand / 48
poj.df$weekly_proc_maint <- (4 * 8000000 + 2500 * poj.df$weekly_demand) / 48

poj.df$manufacturing_cost <- 2000 * poj.df$weekly_demand

# Add in raw material cost
poj.df$raw_material_cost <- poj.df$weekly_demand * 2000 * c(
    rep(mean.over.months[mean.over.months$grove == 'FLA', ]$mean_month,
        48),
    rep(mean.over.months[mean.over.months$grove == 'TEX', ]$mean_month,
        12),
    rep(mean.over.months[mean.over.months$grove == 'CAL', ]$mean_month,
        24))


poj.df$profit <- poj.df$revenue - (poj.df$tanker_car_weekly_purchase_cost +
    poj.df$tanker_car_weekly_travel_cost +
    poj.df$g_p_weekly_cost + poj.df$storage_market_weekly_cost +
    poj.df$manufacturing_cost +
    poj.df$weekly_proc_build +
    poj.df$weekly_proc_maint +
    poj.df$raw_material_cost)
write.csv(poj.df, file='poj_demand_opt.csv',
          quote=FALSE, row.names=FALSE)
ggplot(poj.df, aes(x=price, y=profit, colour=region)) +
    geom_point() + geom_line() +
    ggtitle('POJ Profit (Revenue - Trans. - Man. Costs)')
ggsave('poj_clean_profit_opt.png', width=10, height=6)

poj.profit.max <- poj.df %>% group_by(region) %>%
    filter(profit == max(profit)) %>% select(-month)
write.csv(poj.profit.max, file='poj_max_profit_opt.csv',
          quote=FALSE, row.names=FALSE)


# ROJ
roj.df <- read.csv('roj_demand.csv')
roj.df <- roj.df %>%
    mutate(revenue=2000 * price * demand,
           month=ordered(month,
                         levels=c('Jan', 'Feb', 'Mar', 'Apr',
                         'May', 'Jun', 'Jul', 'Aug',
                         'Sep', 'Oct', 'Nov', 'Dec')),
           weekly_demand = demand / 4)

# Add storage to market distances
roj.df$storage_dist <- c(rep(479.1429, 12),
                         rep(286.7647, 12),
                         rep(712.1667, 12),
                         rep(368.5909, 12),
                         rep(413.3750, 12),
                         rep(659.1250, 12),
                         rep(659, 12))

# Instead of grove to storage, now we have grove to plant and
# plant to storage distances.  We can make similar "efficiency"
# assumptions, where P2->S35, P3->S51, P5->S59, P9->S73.
# We'll ship raw ORA from TEX->P2, CAL->P5, FLA->P3, FLA->P9.

# TEX->P2 = 381
# CAL->P5 = 351
# FLA->P3 = 773
# FLA->P9 = 1528
roj.df$g_p_dist <- c(rep(773, 36),
                     rep(1528, 12),
                     rep(381, 12),
                     rep(351, 24))

# P2 -> S35 = 140
# P3 -> S51 = 317
# P5 -> S59 = 393
# P9 -> S73 = 98

roj.df$p_s_dist <- c(rep(317, 36),
                     rep(98, 12),
                     rep(140, 12),
                     rep(393, 24))
# For tanker car cost, we need to calculate how many tanker
# cars the given demand would require, multiply by its purchase
# cost, and then add the weekly traveling cost.  We'll spread the
# one time purchase cost over weeks by dividing it by 48.

roj.df$num_tanker_cars_needed <- roj.df$weekly_demand / 30
roj.df$tanker_car_weekly_purchase_cost <- 
    roj.df$num_tanker_cars_needed * 100000 / 48
roj.df$tanker_car_weekly_travel_cost <- 36 *
    roj.df$num_tanker_cars_needed * roj.df$p_s_dist

roj.df$g_p_weekly_cost <- 0.22 * roj.df$weekly_demand * roj.df$g_p_dist
roj.df$storage_market_weekly_cost <- 1.2 * roj.df$weekly_demand *
    roj.df$storage_dist

# Also include cost to buy capacity and maintain necessary
# processing. There's a one-time upgrade cost and an every-year
# maintenance. Divide the one-time cost by 48 to "week-ize" it.
roj.df$weekly_proc_build <- 8000 * roj.df$weekly_demand / 48
roj.df$weekly_proc_maint <- (4 * 8000000 + 2500 * roj.df$weekly_demand) / 48

# Reconstitution cost
roj.df$reconstitution_cost <- 650 * roj.df$weekly_demand

# Add in raw material cost
roj.df$raw_material_cost <- roj.df$weekly_demand * 2000 * c(
    rep(mean.over.months[mean.over.months$grove == 'FLA', ]$mean_month,
        48),
    rep(mean.over.months[mean.over.months$grove == 'TEX', ]$mean_month,
        12),
    rep(mean.over.months[mean.over.months$grove == 'CAL', ]$mean_month,
        24))

# Also, add in manufacturing cost of FCOJ because we need to make
# FCOJ to get ROJ (assume no futures).
roj.df$manufacturing_cost <- 2000 * roj.df$weekly_demand

roj.df$profit <- roj.df$revenue - (roj.df$tanker_car_weekly_purchase_cost +
    roj.df$tanker_car_weekly_travel_cost +
    roj.df$g_p_weekly_cost + roj.df$storage_market_weekly_cost +
    roj.df$reconstitution_cost +
    roj.df$weekly_proc_build +
    roj.df$weekly_proc_maint +
    roj.df$raw_material_cost +
    roj.df$manufacturing_cost)
write.csv(roj.df, file='roj_demand_opt.csv',
          quote=FALSE, row.names=FALSE)
ggplot(roj.df, aes(x=price, y=profit, colour=region)) +
    geom_point() + geom_line() +
    ggtitle('ROJ Profit (Revenue - Trans. - Man. Costs)')
ggsave('roj_clean_profit_opt.png', width=10, height=6)

roj.profit.max <- roj.df %>% group_by(region) %>%
    filter(profit == max(profit)) %>% select(-month)
write.csv(roj.profit.max, file='roj_max_profit_opt.csv',
          quote=FALSE, row.names=FALSE)



# FCOJ
fcoj.df <- read.csv('fcoj_demand.csv')
fcoj.df <- fcoj.df %>%
    mutate(revenue=2000 * price * demand,
           month=ordered(month,
                         levels=c('Jan', 'Feb', 'Mar', 'Apr',
                         'May', 'Jun', 'Jul', 'Aug',
                         'Sep', 'Oct', 'Nov', 'Dec')),
           weekly_demand = demand / 4)

# Add storage to market distances
fcoj.df$storage_dist <- c(rep(479.1429, 12),
                         rep(286.7647, 12),
                         rep(712.1667, 12),
                         rep(368.5909, 12),
                         rep(413.3750, 12),
                         rep(659.1250, 12),
                         rep(659, 12))

# Instead of grove to storage, now we have grove to plant and
# plant to storage distances.  We can make similar "efficiency"
# assumptions, where P2->S35, P3->S51, P5->S59, P9->S73.
# We'll ship raw ORA from TEX->P2, CAL->P5, FLA->P3, FLA->P9.

# TEX->P2 = 381
# CAL->P5 = 351
# FLA->P3 = 773
# FLA->P9 = 1528
fcoj.df$g_p_dist <- c(rep(773, 36),
                     rep(1528, 12),
                     rep(381, 12),
                     rep(351, 24))

# P2 -> S35 = 140
# P3 -> S51 = 317
# P5 -> S59 = 393
# P9 -> S73 = 98

fcoj.df$p_s_dist <- c(rep(317, 36),
                     rep(98, 12),
                     rep(140, 12),
                     rep(393, 24))
# For tanker car cost, we need to calculate how many tanker
# cars the given demand would require, multiply by its purchase
# cost, and then add the weekly traveling cost.  We'll spread the
# one time purchase cost over weeks by dividing it by 48.
fcoj.df$num_tanker_cars_needed <- fcoj.df$weekly_demand / 30
fcoj.df$tanker_car_weekly_purchase_cost <- 
    fcoj.df$num_tanker_cars_needed * 100000 / 48
fcoj.df$tanker_car_weekly_travel_cost <- 36 *
    fcoj.df$num_tanker_cars_needed * fcoj.df$p_s_dist

fcoj.df$g_p_weekly_cost <- 0.22 * fcoj.df$weekly_demand * fcoj.df$g_p_dist
fcoj.df$storage_market_weekly_cost <- 1.2 * fcoj.df$weekly_demand *
    fcoj.df$storage_dist

fcoj.df$weekly_proc_build <- 8000 * fcoj.df$weekly_demand / 48
fcoj.df$weekly_proc_maint <- (4 * 8000000 + 2500 * fcoj.df$weekly_demand) / 48

fcoj.df$manufacturing_cost <- 2000 * fcoj.df$weekly_demand

fcoj.df$raw_material_cost <- fcoj.df$weekly_demand * 2000 * c(
    rep(mean.over.months[mean.over.months$grove == 'FLA', ]$mean_month,
        48),
    rep(mean.over.months[mean.over.months$grove == 'TEX', ]$mean_month,
        12),
    rep(mean.over.months[mean.over.months$grove == 'CAL', ]$mean_month,
        24))

fcoj.df$profit <- fcoj.df$revenue - (fcoj.df$tanker_car_weekly_purchase_cost +
    fcoj.df$tanker_car_weekly_travel_cost +
    fcoj.df$g_p_weekly_cost + fcoj.df$storage_market_weekly_cost +
    fcoj.df$manufacturing_cost +
    fcoj.df$weekly_proc_build +
    fcoj.df$weekly_proc_maint +
    fcoj.df$raw_material_cost)
write.csv(fcoj.df, file='fcoj_demand_opt.csv',
          quote=FALSE, row.names=FALSE)
ggplot(fcoj.df, aes(x=price, y=profit, colour=region)) +
    geom_point() + geom_line() +
    ggtitle('FCOJ Profit (Revenue - Trans. - Man. Costs)')
ggsave('fcoj_clean_profit_opt.png', width=10, height=6)

fcoj.profit.max <- fcoj.df %>% group_by(region) %>%
    filter(profit == max(profit)) %>% select(-month)
write.csv(fcoj.profit.max, file='fcoj_max_profit_opt.csv',
          quote=FALSE, row.names=FALSE)