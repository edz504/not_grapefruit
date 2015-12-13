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

ggplot(ora.df, aes(x=price, y=revenue, colour=region)) +
    geom_point() + geom_line() +
    scale_y_continuous(breaks=seq(0, 13000000, 1000000)) +
    ggtitle('ORA Revenue vs. Price, over all regions')
ggsave('ora_clean_rev.png', width=10, height=6)

ora.rev.max <- ora.df %>% group_by(region) %>%
    filter(revenue == max(revenue)) %>% select(-month)
write.csv(ora.rev.max, file='ora_max_rev.csv',
          quote=FALSE, row.names=FALSE)

# We want to maximize profit, not revenue.
# Calculate transportation costs for each price + region.
# Each region has a mean distance for its markets to the closest
# storage.  Let's also assume that for grove to storage, we'll
# ship spot purchases from CAL, ARZ, TEX to S15 and
# FLA (and BRA, SPA) to S61.

# FLA -> S61 = 1143
# CAL -> S15 = 1551
# TEX -> S15 = 96
# ARZ -> S15 = 1189
s15.grove.dist <- mean(c(1551, 96, 1189))
s61.grove.dist <- 1143

region.storage <- read.csv('region_storage_dists.csv')
ora.df$storage_dist <- c(rep(422.7143, 12),
                         rep(359, 12),
                         rep(879, 12),
                         rep(772.6364, 12),
                         rep(469.25, 12),
                         rep(1700.75, 12),
                         rep(1665.1818, 12))
ora.df$grove_dist <- c(rep(s61.grove.dist, 48),
                       rep(s15.grove.dist, 36))
ora.df$weekly_transp_cost <- ora.df$weekly_demand *
  (0.22 * ora.df$grove_dist + 1.2 * ora.df$storage_dist)

# Note: this "profit" only takes into account transportation costs.
ora.df$profit <- ora.df$revenue - ora.df$weekly_transp_cost
ggplot(ora.df, aes(x=price, y=profit, colour=region)) +
    geom_point() + geom_line() +
    ggtitle('ORA Profit (Revenue - Trans. Costs)')
ggsave('ora_clean_profit.png', width=10, height=6)

ora.profit.max <- ora.df %>% group_by(region) %>%
    filter(profit == max(profit)) %>% select(-month)
write.csv(ora.profit.max, file='ora_max_profit.csv',
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

poj.rev.max <- poj.df %>% group_by(region) %>%
    filter(revenue == max(revenue)) %>% select(-month)
write.csv(poj.rev.max, file='poj_max_rev.csv',
          quote=FALSE, row.names=FALSE)

# Add storage to market distances
poj.df$storage_dist <- c(rep(422.7143, 12),
                         rep(359, 12),
                         rep(879, 12),
                         rep(772.6364, 12),
                         rep(469.25, 12),
                         rep(1700.75, 12),
                         rep(1665.1818, 12))

# Instead of grove to storage, now we have grove to plant and
# plant to storage distances.  We can make similar "efficiency"
# assumptions, where P01 sends everything to S61, P05 sends
# everything to S15, and P07 splits evenly between the two.
# We'll ship raw ORA from CAL and ARZ to P05, FLA to P01, and
# TEX to P07.

# FLA -> P01 = 454
# CAL -> P05 = 351
# TEX -> P07 = 1154
# ARZ -> P05 = 88
poj.df$g_p_dist <- c(rep(454 + 1154, 48), rep(351 + 88, 36))

# P1 -> S61 = 718
# P5 -> S15 = 1225
# P7 -> S15 = 1245
# P7 -> S61 = 495
poj.df$p_s_dist <- c(rep(718 + 495, 48), rep(1225 + 1245, 36))
# For tanker car cost, we need to calculate how many tanker
# cars the given demand would require, multiply by its purchase
# cost, and then add the weekly traveling cost.  We'll spread the
# one time purchase cost over weeks by dividing it by 48.

# poj.df$num_tanker_cars_needed <- poj.df$weekly_demand / 30
# poj.df$tanker_car_weekly_purchase_cost <- 
#     poj.df$num_tanker_cars_needed * 100000 / 48
# poj.df$tanker_car_weekly_travel_cost <- 36 *
#     poj.df$num_tanker_cars_needed * poj.df$p_s_dist

# ^ Actually, since our purchases won't matter, let's just use the
# tanker cars already there, in the proportions that we're sending
# them.
poj.df$tanker_cars_used <- c(rep(53 * 0.5 + 11, 48),
                             rep(53 * 0.5 + 22, 36))
poj.df$tanker_car_weekly_travel_cost <- 36 * poj.df$tanker_cars_used *
    poj.df$p_s_dist
poj.df$g_p_weekly_cost <- 0.22 * poj.df$weekly_demand * poj.df$g_p_dist
poj.df$storage_market_weekly_cost <- 1.2 * poj.df$weekly_demand *
    poj.df$storage_dist
poj.df$manufacturing_cost <- 2000 * poj.df$weekly_demand

poj.df$profit <- poj.df$revenue - (poj.df$tanker_car_weekly_travel_cost +
    poj.df$g_p_weekly_cost + poj.df$storage_market_weekly_cost +
    poj.df$manufacturing_cost)
ggplot(poj.df, aes(x=price, y=profit, colour=region)) +
    geom_point() + geom_line() +
    ggtitle('POJ Profit (Revenue - Trans. - Man. Costs)')
ggsave('poj_clean_profit.png', width=10, height=6)

poj.profit.max <- poj.df %>% group_by(region) %>%
    filter(profit == max(profit)) %>% select(-month)
write.csv(poj.profit.max, file='poj_max_profit.csv',
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

ggplot(roj.df, aes(x=price, y=revenue, colour=region)) +
  geom_point() + geom_line() +
  scale_y_continuous(breaks=seq(0, 13000000, 1000000)) +
  ggtitle('ROJ Revenue vs. Price, over all regions')
ggsave('roj_clean_rev.png', width=10, height=6)

roj.rev.max <- roj.df %>% group_by(region) %>%
  filter(revenue == max(revenue)) %>% select(-month)
write.csv(roj.rev.max, file='roj_max_rev.csv',
          quote=FALSE, row.names=FALSE)

# Add storage to market distances
roj.df$storage_dist <- c(rep(422.7143, 12),
                         rep(359, 12),
                         rep(879, 12),
                         rep(772.6364, 12),
                         rep(469.25, 12),
                         rep(1700.75, 12),
                         rep(1665.1818, 12))

# Instead of grove to storage, now we have grove to plant and
# plant to storage distances.  We can make similar "efficiency"
# assumptions, where P01 sends everything to S61, P05 sends
# everything to S15, and P07 splits evenly between the two.
# We'll ship raw ORA from CAL and ARZ to P05, FLA to P01, and
# TEX to P07.

# FLA -> P01 = 454
# CAL -> P05 = 351
# TEX -> P07 = 1154
# ARZ -> P05 = 88
roj.df$g_p_dist <- c(rep(454 + 1154, 48), rep(351 + 88, 36))

# P1 -> S61 = 718
# P5 -> S15 = 1225
# P7 -> S15 = 1245
# P7 -> S61 = 495
roj.df$p_s_dist <- c(rep(718 + 495, 48), rep(1225 + 1245, 36))
# For tanker car cost, we need to calculate how many tanker
# cars the given demand would require, multiply by its purchase
# cost, and then add the weekly traveling cost.  We'll spread the
# one time purchase cost over weeks by dividing it by 48.

# poj.df$num_tanker_cars_needed <- poj.df$weekly_demand / 30
# poj.df$tanker_car_weekly_purchase_cost <- 
#     poj.df$num_tanker_cars_needed * 100000 / 48
# poj.df$tanker_car_weekly_travel_cost <- 36 *
#     poj.df$num_tanker_cars_needed * poj.df$p_s_dist

# ^ Actually, since our purchases won't matter, let's just use the
# tanker cars already there, in the proportions that we're sending
# them.
roj.df$tanker_cars_used <- c(rep(53 * 0.5 + 11, 48),
                             rep(53 * 0.5 + 22, 36))
roj.df$tanker_car_weekly_travel_cost <- 36 * roj.df$tanker_cars_used *
  roj.df$p_s_dist
roj.df$g_p_weekly_cost <- 0.22 * roj.df$weekly_demand * roj.df$g_p_dist
roj.df$storage_market_weekly_cost <- 1.2 * roj.df$weekly_demand *
  roj.df$storage_dist
roj.df$reconstitution_cost <- 650 * roj.df$weekly_demand

roj.df$profit <- roj.df$revenue - (roj.df$tanker_car_weekly_travel_cost +
                                     roj.df$g_p_weekly_cost + roj.df$storage_market_weekly_cost +
                                     roj.df$reconstitution_cost)
ggplot(roj.df, aes(x=price, y=profit, colour=region)) +
  geom_point() + geom_line() +
  ggtitle('ROJ Profit (Revenue - Trans. - Man. Costs)')
ggsave('roj_clean_profit.png', width=10, height=6)

roj.profit.max <- roj.df %>% group_by(region) %>%
  filter(profit == max(profit)) %>% select(-month)
write.csv(roj.profit.max, file='roj_max_profit.csv',
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

ggplot(fcoj.df, aes(x=price, y=revenue, colour=region)) +
  geom_point() + geom_line() +
  scale_y_continuous(breaks=seq(0, 13000000, 1000000)) +
  ggtitle('FCOJ Revenue vs. Price, over all regions')
ggsave('fcoj_clean_rev.png', width=10, height=6)

fcoj.rev.max <- fcoj.df %>% group_by(region) %>%
  filter(revenue == max(revenue)) %>% select(-month)
write.csv(fcoj.rev.max, file='fcoj_max_rev.csv',
          quote=FALSE, row.names=FALSE)

# Add storage to market distances
fcoj.df$storage_dist <- c(rep(422.7143, 12),
                         rep(359, 12),
                         rep(879, 12),
                         rep(772.6364, 12),
                         rep(469.25, 12),
                         rep(1700.75, 12),
                         rep(1665.1818, 12))

# Instead of grove to storage, now we have grove to plant and
# plant to storage distances.  We can make similar "efficiency"
# assumptions, where P01 sends everything to S61, P05 sends
# everything to S15, and P07 splits evenly between the two.
# We'll ship raw ORA from CAL and ARZ to P05, FLA to P01, and
# TEX to P07.

# FLA -> P01 = 454
# CAL -> P05 = 351
# TEX -> P07 = 1154
# ARZ -> P05 = 88
fcoj.df$g_p_dist <- c(rep(454 + 1154, 48), rep(351 + 88, 36))

# P1 -> S61 = 718
# P5 -> S15 = 1225
# P7 -> S15 = 1245
# P7 -> S61 = 495
fcoj.df$p_s_dist <- c(rep(718 + 495, 48), rep(1225 + 1245, 36))

# ^ Actually, since our purchases won't matter, let's just use the
# tanker cars already there, in the proportions that we're sending
# them.
fcoj.df$tanker_cars_used <- c(rep(53 * 0.5 + 11, 48),
                             rep(53 * 0.5 + 22, 36))
fcoj.df$tanker_car_weekly_travel_cost <- 36 * fcoj.df$tanker_cars_used *
  fcoj.df$p_s_dist
fcoj.df$g_p_weekly_cost <- 0.22 * fcoj.df$weekly_demand * fcoj.df$g_p_dist
fcoj.df$storage_market_weekly_cost <- 1.2 * fcoj.df$weekly_demand *
  fcoj.df$storage_dist
fcoj.df$manufacturing_cost <- 1000 * fcoj.df$weekly_demand

fcoj.df$profit <- fcoj.df$revenue - (fcoj.df$tanker_car_weekly_travel_cost +
                                     fcoj.df$g_p_weekly_cost + fcoj.df$storage_market_weekly_cost +
                                     fcoj.df$manufacturing_cost)
ggplot(fcoj.df, aes(x=price, y=profit, colour=region)) +
  geom_point() + geom_line() +
  ggtitle('FCOJ Profit (Revenue - Trans. - Man. Costs)')
ggsave('fcoj_clean_profit.png', width=10, height=6)

fcoj.profit.max <- fcoj.df %>% group_by(region) %>%
  filter(profit == max(profit)) %>% select(-month)
write.csv(fcoj.profit.max, file='fcoj_max_profit.csv',
          quote=FALSE, row.names=FALSE)


all.df <- rbind(ora.df[, c(3, 4, 11)],
                roj.df[, c(3, 4, 16)],
                fcoj.df[, c(3, 4, 16)],
                poj.df[, c(3, 4, 16)])
all.df$product <- factor(c(rep('ORA', 84),
                           rep('ROJ', 84),
                           rep('FCOJ', 84),
                           rep('POJ', 84)))

ggplot(all.df, aes(x=price, y=profit, colour=product)) +
  geom_line() + geom_point() + facet_wrap(~region, ncol=3)