library(dplyr)

# Change when we switch plans
ora <- read.csv('profit_csvs/ora_max_profit.csv')
poj <- read.csv('profit_csvs/poj_max_profit.csv')
roj <- read.csv('profit_csvs/roj_max_profit.csv')
fcoj <- read.csv('profit_csvs/fcoj_fixed_quantity.csv')

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

print('S35 storage capacity: ')
sum(by.region[by.region$region == 'DS', 2])

print('S59 storage capacity: ')
sum(by.region[by.region$region %in% c('NW', 'SW'), 2])

print('S73 storage capacity: ')
sum(by.region[by.region$region == 'MW', 2])


by.region.proc <- df[df$product %in% c('POJ', 'ROJ'), ] %>%
    group_by(region) %>%
    summarise(proc_capacity=sum(predicted_demand))
print('P03 processing capacity: ')
sum(by.region.proc[by.region.proc$region %in% c('NE', 'MA', 'SE'), 2])

print('P02 processing capacity: ')
sum(by.region.proc[by.region.proc$region == 'DS', 2])

print('P05 processing capacity: ')
sum(by.region.proc[by.region.proc$region %in% c('NW', 'SW'), 2])

print('P09 processing capacity: ')
sum(by.region.proc[by.region.proc$region == 'MW', 2])


# FLA weekly spot purchase
fla <- df[(df$region %in% c('NE', 'MA', 'SE', 'MW')) &
           df$product %in% c('ORA', 'POJ', 'ROJ'), ]
sum(fla$predicted_demand)

# CAL weekly spot purchase
cal <- df[(df$region %in% c('SW', 'NW')) &
           df$product %in% c('ORA', 'POJ', 'ROJ'), ]
sum(cal$predicted_demand)

# TEX weekly spot purchase
tex <- df[(df$region %in% c('DS')) &
           df$product %in% c('ORA', 'POJ', 'ROJ'), ]
sum(tex$predicted_demand)


# Calculate futures to order
roj.futures <- read.csv('profit_csvs/roj_futures_max_profit.csv')
fcoj.futures <- read.csv('profit_csvs/fcoj_futures_max_profit.csv')
sum(roj.futures$predicted_demand + fcoj.futures$predicted_demand) * 48


# Calculate grove shipping proportions
fla.p03 <- sum(df[(df$region %in% c('NE', 'MA', 'SE')) &
                   df$product %in% c('POJ', 'ROJ'),]$predicted_demand) /
           sum(fla$predicted_demand)
fla.p03
fla.p09 <- sum(df[(df$region %in% c('MW')) &
                   df$product %in% c('POJ', 'ROJ'),]$predicted_demand) /
           sum(fla$predicted_demand)
fla.p09
fla.s51 <- sum(df[(df$region %in% c('NE', 'MA', 'SE')) &
                   df$product %in% c('ORA'),]$predicted_demand) /
           sum(fla$predicted_demand)
fla.s51
fla.s73 <- sum(df[(df$region %in% c('MW')) &
                   df$product %in% c('ORA'),]$predicted_demand) /
           sum(fla$predicted_demand)
fla.s73

cal.p05 <- sum(df[(df$region %in% c('NW', 'SW')) &
                   df$product %in% c('POJ', 'ROJ'),]$predicted_demand) /
           sum(cal$predicted_demand)
cal.p05
cal.s59 <- sum(df[(df$region %in% c('NW', 'SW')) &
                   df$product %in% c('ORA'),]$predicted_demand) /
           sum(cal$predicted_demand)
cal.s59

tex.p02 <- sum(df[(df$region %in% c('DS')) &
                   df$product %in% c('POJ', 'ROJ'),]$predicted_demand) /
           sum(tex$predicted_demand)
tex.p02
tex.s35 <- sum(df[(df$region %in% c('DS')) &
                   df$product %in% c('ORA'),]$predicted_demand) /
           sum(tex$predicted_demand)
tex.s35


# Manufacturing ratios
p02.manu <- sum(df[(df$region %in% c('DS')) &
                   df$product %in% c('POJ'),]$predicted_demand) /
            sum(df[(df$region %in% c('DS')) &
                   df$product %in% c('POJ', 'ROJ'),]$predicted_demand)
p02.manu

p03.manu <- sum(df[(df$region %in% c('NE', 'MA', 'SE')) &
                   df$product %in% c('POJ'),]$predicted_demand) /
            sum(df[(df$region %in% c('NE', 'MA', 'SE')) &
                   df$product %in% c('POJ', 'ROJ'),]$predicted_demand)
p03.manu

p05.manu <- sum(df[(df$region %in% c('NW', 'SW')) &
                   df$product %in% c('POJ'),]$predicted_demand) /
            sum(df[(df$region %in% c('NW', 'SW')) &
                   df$product %in% c('POJ', 'ROJ'),]$predicted_demand)
p05.manu

p09.manu <- sum(df[(df$region %in% c('MW')) &
                   df$product %in% c('POJ'),]$predicted_demand) /
            sum(df[(df$region %in% c('MW')) &
                   df$product %in% c('POJ', 'ROJ'),]$predicted_demand)
p09.manu

# Futures shipping ratios
s35.fcoj.futures.ship <- sum(df[(df$product == 'FCOJ' &
                                 df$region == 'DS'), ]$predicted_demand) /
                         sum(df[df$product == 'FCOJ', ]$predicted_demand)
s35.fcoj.futures.ship

s51.fcoj.futures.ship <- sum(df[(df$product == 'FCOJ' &
                                 df$region %in% c('NE', 'MA', 'SE')),]$predicted_demand) /
                         sum(df[df$product == 'FCOJ', ]$predicted_demand)
s51.fcoj.futures.ship

s59.fcoj.futures.ship <- sum(df[(df$product == 'FCOJ' &
                                 df$region %in% c('NW', 'SW')), ]$predicted_demand) /
                         sum(df[df$product == 'FCOJ', ]$predicted_demand)
s59.fcoj.futures.ship

s73.fcoj.futures.ship <- sum(df[(df$product == 'FCOJ' &
                                 df$region == 'MW'), ]$predicted_demand) /
                         sum(df[df$product == 'FCOJ', ]$predicted_demand)
s73.fcoj.futures.ship

# Reconstitution
s35.recon <- sum(df[(df$product == 'ROJ' &
                     df$region == 'DS'), ]$predicted_demand) /
             sum(df[(df$product %in% c('ROJ', 'FCOJ') &
                     df$region == 'DS'), ]$predicted_demand)
s35.recon

s51.recon <- sum(df[(df$product == 'ROJ' &
                     df$region %in% c('NE', 'MA', 'SE')), ]$predicted_demand) /
             sum(df[(df$product %in% c('ROJ', 'FCOJ') &
                     df$region %in% c('NE', 'MA', 'SE')), ]$predicted_demand)
s51.recon

s59.recon <- sum(df[(df$product == 'ROJ' &
                     df$region %in% c('NW', 'SW')), ]$predicted_demand) /
             sum(df[(df$product %in% c('ROJ', 'FCOJ') &
                     df$region %in% c('NW', 'SW')), ]$predicted_demand)
s59.recon

s73.recon <- sum(df[(df$product == 'ROJ' &
                     df$region == 'MW'), ]$predicted_demand) /
             sum(df[(df$product %in% c('ROJ', 'FCOJ') &
                     df$region == 'MW'), ]$predicted_demand)
s73.recon