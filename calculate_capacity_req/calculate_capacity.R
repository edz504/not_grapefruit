library(dplyr)

cwd <- getwd()
setwd('..')
ora <- read.csv('fit_demand/profit_csvs/ora_max_profit.csv')
poj <- read.csv('fit_demand/profit_csvs/poj_max_profit.csv')
roj <- read.csv('fit_demand/profit_csvs/roj_max_profit.csv')
fcoj <- read.csv('futures_delivery_136k/optimal_fcoj_136k.csv')

df <- rbind(ora[, c(1:4, ncol(ora))],
            poj[, c(1:4, ncol(poj))],
            roj[, c(1:4, ncol(roj))],
            fcoj[, c(1:4, ncol(fcoj))])
df$region <- sapply(df$region, as.character)
df$product <- sapply(df$product, as.character)

by.region <- df %>% group_by(region) %>%
    summarise(storage_capacity=sum(predicted_demand))

print('S51 storage capacity: ')
sum(by.region[by.region$region %in% c('NE', 'MA', 'SE'), 2])
# 3000

print('S35 storage capacity: ')
sum(by.region[by.region$region == 'DS', 2])
# 1000

print('S59 storage capacity: ')
sum(by.region[by.region$region %in% c('NW', 'SW'), 2])
# 750

print('S73 storage capacity: ')
sum(by.region[by.region$region == 'MW', 2])
# 1400


by.region.proc <- df[df$product %in% c('POJ', 'ROJ'), ] %>% group_by(region) %>%
    summarise(proc_capacity=sum(predicted_demand))
print('P03 processing capacity: ')
sum(by.region.proc[by.region.proc$region %in% c('NE', 'MA', 'SE'), 2])
# 750

print('P02 processing capacity: ')
sum(by.region.proc[by.region.proc$region == 'DS', 2])
# 250

print('P05 processing capacity: ')
sum(by.region.proc[by.region.proc$region %in% c('NW', 'SW'), 2])
# 250

print('P09 processing capacity: ')
sum(by.region.proc[by.region.proc$region == 'MW', 2])
# 250