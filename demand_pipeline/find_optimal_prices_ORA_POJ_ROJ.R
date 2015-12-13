library(ggplot2)
library(dplyr)

all.predicted.demands <- read.csv('all_predicted_demands.csv',
    stringsAsFactors=FALSE)
ora.df <- all.predicted.demands[all.predicted.demands$product == 'ORA',]

# ORA
ora.df <- ora.df %>%
    mutate(revenue=2000 * price * predicted_demand,
           weekly_demand = predicted_demand)

s35.grove.dist <- 266
s51.grove.dist <- 967
s59.grove.dist <- 176
s73.grove.dist <- 1470
ora.df$grove_dist <- c(rep(s51.grove.dist, 903),
                       rep(s73.grove.dist, 301),
                       rep(s35.grove.dist, 301),
                       rep(s59.grove.dist, 602))

# We have 301 rows per region (in the order NE, MA, SE, MW, DS, NW, SW)
region.storage <- read.csv('region_storage_dists_opt.csv')
ora.df$storage_dist <- c(rep(479.1429, 301),
                         rep(286.7647, 301),
                         rep(712.1667, 301),
                         rep(368.5909, 301),
                         rep(413.3750, 301),
                         rep(659.1250, 301),
                         rep(659, 301))
ora.df$weekly_transp_cost <- ora.df$weekly_demand *
  (0.22 * ora.df$grove_dist + 1.2 * ora.df$storage_dist)

# Also include cost to buy capacity and maintain necessary
# storage. There's a one-time upgrade cost and an every-year
# maintenance. Divide the one-time cost by 48 to "week-ize" it.
ora.df$weekly_storage_build <- 6000 * ora.df$weekly_demand / 48
ora.df$weekly_storage_maint <- (650 * ora.df$weekly_demand) / 48
# ^ Note that we do not account for the 7.5m * 4 because it will
# be present at every price (add in at end).

# Finally, include the raw material cost (spot purchase of ORA).
# We use our mean belief for each grove's spot purchase price.
# (FLA x 36, FLA x 12, TEX x 12, CAL x 24) is the vectoring.
# Average over months for now, disregarding seasonality -- also,
# no need to factor in exchange rates for now, assume we buy from
# FLA, not FLA / BRA / SPA.

cwd <- getwd()
setwd('..') # move up one directory
mean.raw.price.beliefs <- read.csv(
    'grove_beliefs/raw_price_beliefs_mean.csv')
setwd(cwd)

mean.over.months <- mean.raw.price.beliefs %>%
    group_by(grove) %>%
    summarise(mean_month=mean(price))
ora.df$raw_material_cost <- ora.df$weekly_demand * 2000 * c(
    rep(mean.over.months[mean.over.months$grove == 'FLA', ]$mean_month,
        4 * 301),
    rep(mean.over.months[mean.over.months$grove == 'TEX', ]$mean_month,
        301),
    rep(mean.over.months[mean.over.months$grove == 'CAL', ]$mean_month,
        2 * 301))

# Note: this "profit" is for the first year, actual profit
# should be even higher in later years when we don't have the
# capacity cost.
ora.df$year1_profit <- ora.df$revenue - (ora.df$weekly_transp_cost +
    ora.df$weekly_storage_build + ora.df$weekly_storage_maint +
    ora.df$raw_material_cost)
ora.df$profit <- ora.df$revenue - (ora.df$weekly_transp_cost +
    ora.df$weekly_storage_maint +
    ora.df$raw_material_cost)
ggplot(ora.df, aes(x=price, colour=region)) +
    geom_line(aes(y=year1_profit), linetype='dotted') +
    geom_line(aes(y=profit)) +
    ggtitle('ORA Profit (Year 1 and After)')
ggsave('profit_curves/ora_profit.png', width=10, height=6)

ora.profit.max <- ora.df %>% group_by(region) %>%
    filter(profit == max(profit))
write.csv(ora.profit.max, file='profit_csvs/ora_max_profit.csv',
          quote=FALSE, row.names=FALSE)


# POJ
poj.df <- all.predicted.demands[all.predicted.demands$product == 'POJ',]
poj.df <- poj.df %>%
    mutate(revenue=2000 * price * predicted_demand,
           weekly_demand = predicted_demand)

# Add storage to market distances
poj.df$storage_dist <- c(rep(479.1429, 301),
                         rep(286.7647, 301),
                         rep(712.1667, 301),
                         rep(368.5909, 301),
                         rep(413.3750, 301),
                         rep(659.1250, 301),
                         rep(659, 301))

# Instead of grove to storage, now we have grove to plant and
# plant to storage distances.  We can make similar "efficiency"
# assumptions, where P2->S35, P3->S51, P5->S59, P9->S73.
# We'll ship raw ORA from TEX->P2, CAL->P5, FLA->P3, FLA->P9.

# TEX->P2 = 381
# CAL->P5 = 351
# FLA->P3 = 773
# FLA->P9 = 1528
poj.df$g_p_dist <- c(rep(773, 903),
                     rep(1528, 301),
                     rep(381, 301),
                     rep(351, 602))

# P2 -> S35 = 140
# P3 -> S51 = 317
# P5 -> S59 = 393
# P9 -> S73 = 98
poj.df$p_s_dist <- c(rep(317, 903),
                     rep(98, 301),
                     rep(140, 301),
                     rep(393, 602))

# For tanker car cost, we need to calculate how many tanker
# cars the given demand would require, multiply by its purchase
# cost, and then add the weekly traveling cost.  We'll spread the
# one time purchase cost over weeks by dividing it by 48.
poj.df$num_tanker_cars_needed <- 2 * poj.df$weekly_demand / 30
poj.df$tanker_car_weekly_purchase_cost <- 
    poj.df$num_tanker_cars_needed * 100000 / 48
poj.df$tanker_car_weekly_travel_cost <- 36 *
    0.5 * poj.df$num_tanker_cars_needed * poj.df$p_s_dist
poj.df$tanker_car_weekly_hold_cost <- 10 *
    0.5 * poj.df$num_tanker_cars_needed

poj.df$g_p_weekly_cost <- 0.22 * poj.df$weekly_demand * poj.df$g_p_dist
poj.df$storage_market_weekly_cost <- 1.2 * poj.df$weekly_demand *
    poj.df$storage_dist

# Also include cost to buy capacity and maintain necessary
# processing. There's a one-time upgrade cost and an every-year
# maintenance. Divide the one-time cost by 48 to "week-ize" it.
poj.df$weekly_proc_build <- 8000 * poj.df$weekly_demand / 48
poj.df$weekly_proc_maint <- (2500 * poj.df$weekly_demand) / 48
# Note that we do not add in the $8m * 4 processing maintenance,
# because it will be there for all prices (and we're 2x-counting it
# for the other products)
poj.df$weekly_storage_build <- 6000 * poj.df$weekly_demand / 48
poj.df$weekly_storage_maint <- (650 * poj.df$weekly_demand) / 48

poj.df$manufacturing_cost <- 2000 * poj.df$weekly_demand

# Add in raw material cost
poj.df$raw_material_cost <- poj.df$weekly_demand * 2000 * c(
    rep(mean.over.months[mean.over.months$grove == 'FLA', ]$mean_month,
        4 * 301),
    rep(mean.over.months[mean.over.months$grove == 'TEX', ]$mean_month,
        301),
    rep(mean.over.months[mean.over.months$grove == 'CAL', ]$mean_month,
        2 * 301))


poj.df$year1_profit <- poj.df$revenue - (
    poj.df$tanker_car_weekly_purchase_cost +
    poj.df$tanker_car_weekly_travel_cost +
    poj.df$tanker_car_weekly_hold_cost +
    poj.df$g_p_weekly_cost +
    poj.df$storage_market_weekly_cost +
    poj.df$manufacturing_cost +
    poj.df$weekly_proc_build +
    poj.df$weekly_proc_maint +
    poj.df$raw_material_cost +
    poj.df$weekly_storage_build +
    poj.df$weekly_storage_maint)
poj.df$profit <- poj.df$year1_profit + (
     poj.df$tanker_car_weekly_purchase_cost +
     poj.df$weekly_proc_build +
     poj.df$weekly_storage_build
     )
ggplot(poj.df, aes(x=price, colour=region)) +
    geom_line(aes(y=year1_profit), linetype='dotted') +
    geom_line(aes(y=profit)) +
    ggtitle('POJ Profit (Year 1 and After)')
ggsave('profit_curves/poj_profit.png', width=10, height=6)

poj.profit.max <- poj.df %>% group_by(region) %>%
    filter(profit == max(profit))
write.csv(poj.profit.max, file='profit_csvs/poj_max_profit.csv',
          quote=FALSE, row.names=FALSE)



#### The other two products are price-optimized using futures

# ROJ
roj.df <- all.predicted.demands[all.predicted.demands$product == 'ROJ',]
roj.df <- roj.df %>%
    mutate(revenue=2000 * price * predicted_demand,
           weekly_demand = predicted_demand)

# Add storage to market distances
roj.df$storage_dist <- c(rep(479.1429, 301),
                         rep(286.7647, 301),
                         rep(712.1667, 301),
                         rep(368.5909, 301),
                         rep(413.3750, 301),
                         rep(659.1250, 301),
                         rep(659, 301))

# Instead of grove to storage, now we have grove to plant and
# plant to storage distances.  We can make similar "efficiency"
# assumptions, where P2->S35, P3->S51, P5->S59, P9->S73.
# We'll ship raw ORA from TEX->P2, CAL->P5, FLA->P3, FLA->P9.

# TEX->P2 = 381
# CAL->P5 = 351
# FLA->P3 = 773
# FLA->P9 = 1528
roj.df$g_p_dist <- c(rep(773, 903),
                     rep(1528, 301),
                     rep(381, 301),
                     rep(351, 602))

# P2 -> S35 = 140
# P3 -> S51 = 317
# P5 -> S59 = 393
# P9 -> S73 = 98

roj.df$p_s_dist <- c(rep(317, 903),
                     rep(98, 301),
                     rep(140, 301),
                     rep(393, 602))
# For tanker car cost, we need to calculate how many tanker
# cars the given demand would require, multiply by its purchase
# cost, and then add the weekly traveling cost.  We'll spread the
# one time purchase cost over weeks by dividing it by 48.
roj.df$num_tanker_cars_needed <- 2 * roj.df$weekly_demand / 30
roj.df$tanker_car_weekly_purchase_cost <- 
    roj.df$num_tanker_cars_needed * 100000 / 48
roj.df$tanker_car_weekly_travel_cost <- 36 *
    0.5 * roj.df$num_tanker_cars_needed * roj.df$p_s_dist
roj.df$tanker_car_weekly_hold_cost <- 10 *
    0.5 * roj.df$num_tanker_cars_needed

roj.df$g_p_weekly_cost <- 0.22 * roj.df$weekly_demand * roj.df$g_p_dist
roj.df$storage_market_weekly_cost <- 1.2 * roj.df$weekly_demand *
    roj.df$storage_dist

roj.df$weekly_storage_build <- 6000 * roj.df$weekly_demand / 48
roj.df$weekly_storage_maint <- (650 * roj.df$weekly_demand) / 48
roj.df$weekly_proc_build <- 8000 * roj.df$weekly_demand / 48
roj.df$weekly_proc_maint <- (2500 * roj.df$weekly_demand) / 48

# Reconstitution cost
roj.df$reconstitution_cost <- 650 * roj.df$weekly_demand

# Add in raw material cost
roj.df$raw_material_cost <- roj.df$weekly_demand * 2000 * c(
    rep(mean.over.months[mean.over.months$grove == 'FLA', ]$mean_month,
        4 * 301),
    rep(mean.over.months[mean.over.months$grove == 'TEX', ]$mean_month,
        301),
    rep(mean.over.months[mean.over.months$grove == 'CAL', ]$mean_month,
        2 * 301))

# Also, add in manufacturing cost of FCOJ because we need to make
# FCOJ to get ROJ (assume no futures).
roj.df$manufacturing_cost <- 2000 * roj.df$weekly_demand

roj.df$year1_profit <- roj.df$revenue - (
    roj.df$tanker_car_weekly_purchase_cost +
    roj.df$tanker_car_weekly_travel_cost +
    roj.df$tanker_car_weekly_hold_cost +
    roj.df$g_p_weekly_cost +
    roj.df$storage_market_weekly_cost +
    roj.df$manufacturing_cost +
    roj.df$reconstitution_cost +
    roj.df$weekly_proc_build +
    roj.df$weekly_proc_maint +
    roj.df$raw_material_cost +
    roj.df$weekly_storage_build +
    roj.df$weekly_storage_maint)
roj.df$profit <- roj.df$year1_profit + (
     roj.df$tanker_car_weekly_purchase_cost +
     roj.df$weekly_proc_build +
     roj.df$weekly_storage_build
     )
ggplot(roj.df, aes(x=price, y=profit, colour=region)) +
    geom_line(aes(y=year1_profit), linetype='dotted') +
    geom_line(aes(y=profit)) +
    ggtitle('ROJ Profit (Year 1 and After)')
ggsave('profit_curves/roj_profit.png', width=10, height=6)

roj.profit.max <- roj.df %>% group_by(region) %>%
    filter(profit == max(profit))
write.csv(roj.profit.max, file='profit_csvs/roj_max_profit.csv',
          quote=FALSE, row.names=FALSE)


# # FCOJ
# #### 
# # Note this assumes we manufacture the FCOJ
# ####
# fcoj.df <- all.predicted.demands[all.predicted.demands$product == 'FCOJ',]
# fcoj.df <- fcoj.df %>%
#     mutate(revenue=2000 * price * predicted_demand,
#            weekly_demand = predicted_demand)

# # Add storage to market distances
# fcoj.df$storage_dist <- c(rep(479.1429, 301),
#                          rep(286.7647, 301),
#                          rep(712.1667, 301),
#                          rep(368.5909, 301),
#                          rep(413.3750, 301),
#                          rep(659.1250, 301),
#                          rep(659, 301))

# # Instead of grove to storage, now we have grove to plant and
# # plant to storage distances.  We can make similar "efficiency"
# # assumptions, where P2->S35, P3->S51, P5->S59, P9->S73.
# # We'll ship raw ORA from TEX->P2, CAL->P5, FLA->P3, FLA->P9.

# # TEX->P2 = 381
# # CAL->P5 = 351
# # FLA->P3 = 773
# # FLA->P9 = 1528
# fcoj.df$g_p_dist <- c(rep(773, 903),
#                      rep(1528, 301),
#                      rep(381, 301),
#                      rep(351, 602))

# # P2 -> S35 = 140
# # P3 -> S51 = 317
# # P5 -> S59 = 393
# # P9 -> S73 = 98

# fcoj.df$p_s_dist <- c(rep(317, 903),
#                      rep(98, 301),
#                      rep(140, 301),
#                      rep(393, 602))
# # For tanker car cost, we need to calculate how many tanker
# # cars the given demand would require, multiply by its purchase
# # cost, and then add the weekly traveling cost.  We'll spread the
# # one time purchase cost over weeks by dividing it by 48.
# fcoj.df$num_tanker_cars_needed <- fcoj.df$weekly_demand / 30
# fcoj.df$tanker_car_weekly_purchase_cost <- 
#     fcoj.df$num_tanker_cars_needed * 100000 / 48
# fcoj.df$tanker_car_weekly_travel_cost <- 36 *
#     fcoj.df$num_tanker_cars_needed * fcoj.df$p_s_dist

# fcoj.df$g_p_weekly_cost <- 0.22 * fcoj.df$weekly_demand * fcoj.df$g_p_dist
# fcoj.df$storage_market_weekly_cost <- 1.2 * fcoj.df$weekly_demand *
#     fcoj.df$storage_dist

# fcoj.df$weekly_proc_build <- 8000 * fcoj.df$weekly_demand / 48
# fcoj.df$weekly_proc_maint <- (2500 * fcoj.df$weekly_demand) / 48
# fcoj.df$weekly_storage_build <- 6000 * fcoj.df$weekly_demand / 48
# fcoj.df$weekly_storage_maint <- (650 * fcoj.df$weekly_demand) / 48

# fcoj.df$manufacturing_cost <- 2000 * fcoj.df$weekly_demand

# fcoj.df$raw_material_cost <- fcoj.df$weekly_demand * 2000 * c(
#     rep(mean.over.months[mean.over.months$grove == 'FLA', ]$mean_month,
#         4 * 301),
#     rep(mean.over.months[mean.over.months$grove == 'TEX', ]$mean_month,
#         301),
#     rep(mean.over.months[mean.over.months$grove == 'CAL', ]$mean_month,
#         2 * 301))

# fcoj.df$year1_profit <- fcoj.df$revenue - (fcoj.df$tanker_car_weekly_purchase_cost +
#     fcoj.df$tanker_car_weekly_travel_cost +
#     fcoj.df$g_p_weekly_cost + fcoj.df$storage_market_weekly_cost +
#     fcoj.df$manufacturing_cost +
#     fcoj.df$weekly_proc_build +
#     fcoj.df$weekly_proc_maint +
#     fcoj.df$raw_material_cost +
#     fcoj.df$weekly_storage_build +
#     fcoj.df$weekly_storage_maint)
# fcoj.df$profit <- fcoj.df$year1_profit + fcoj.df$weekly_proc_build +
#     fcoj.df$weekly_storage_build
# ggplot(fcoj.df, aes(x=price, y=profit, colour=region)) +
#     geom_line(aes(y=year1_profit), linetype='dotted') +
#     geom_line(aes(y=profit)) +
#     ggtitle('FCOJ Profit (Year 1 and After)')
# ggsave('profit_curves/fcoj_profit.png', width=10, height=6)

# fcoj.profit.max <- fcoj.df %>% group_by(region) %>%
#     filter(profit == max(profit))
# write.csv(fcoj.profit.max, file='profit_csvs/fcoj_max_profit.csv',
#           quote=FALSE, row.names=FALSE)


# # Total profit, using FCOJ futures
# for (fcoj_future_price in seq(0.6, 1.1, 0.1)) {
#     profit <- 48 * (sum(ora.profit.max$profit) + sum(poj.profit.max$profit) +
#         sum(roj.profit.max$profit)) +
#         (6112246 * 48 - fcoj_future_price * 136000 * 2000) -
#         (4 * 7500000 + 4 * 8000000)
#     print(profit)
# }

# sum(ora.profit.max$weekly_demand) + sum(poj.profit.max$weekly_demand) +
#     sum(roj.profit.max$weekly_demand)