library(dplyr)

fcoj.df <- read.csv('fcoj_max_profit_opt.csv')
roj.df <- read.csv('roj_max_profit_opt.csv')
ora.df <- read.csv('ora_max_profit_opt.csv')
poj.df <- read.csv('poj_max_profit_opt.csv')

weekly.demands.df <- rbind(fcoj.df[, c(2, 3, 6)],
                           roj.df[, c(2, 3, 6)],
                           ora.df[, c(2, 3, 6)],
                           poj.df[, c(2, 3, 6)])
weekly.demands.df$product <- factor(c(rep('FCOJ', 7),
                               rep('ROJ', 7),
                               rep('ORA', 7),
                               rep('POJ', 7)))
weekly.demands.df$storage <- factor(rep(c(rep('S51', 3),
                                          'S73',
                                          'S35',
                                          rep('S59', 2)), 4))

storage.weekly.demands <- weekly.demands.df %>%
    group_by(storage, product) %>%
    summarise(total_weekly_demand=sum(weekly_demand))

storage.weekly.demands$plant <- factor(c(rep('P02', 4),
                                         rep('P03', 4),
                                         rep('P05', 4),
                                         rep('P09', 4)))

write.csv(storage.weekly.demands,
          file='weekly_demands_by_storage_opt.csv',
          quote=FALSE, row.names=FALSE)

storage.capacity.req <- storage.weekly.demands %>%
  group_by(storage) %>%
  summarise(storage_capacity_needed=sum(total_weekly_demand))

# Filter out ORA and FCOJ to calculate processing capacity
# requirements.
proc.capacity.req <- storage.weekly.demands %>%
  filter(as.integer(product) > 2) %>%
  group_by(plant) %>%
  summarise(processing_capacity_needed=sum(total_weekly_demand)) %>%
  mutate(tanker_cars_needed = processing_capacity_needed / 30)

weekly.fcoj.demand <- storage.weekly.demands %>%
  filter(as.integer(product) == 1)

annual.fcoj.demand <- sum(fcoj.demand$total_weekly_demand) * 48