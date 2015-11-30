setwd('..')
fcoj.demands.at.profit.max <- read.csv(
    'clean_demand/fcoj_max_profit_opt.csv')

s35.weekly.demand <- fcoj.demands.at.profit.max$weekly_demand[5]
s51.weekly.demand <- sum(
    fcoj.demands.at.profit.max$weekly_demand[c(1, 2, 3)])
s59.weekly.demand <- sum(
    fcoj.demands.at.profit.max$weekly_demand[c(6, 7)])
s73.weekly.demand <- fcoj.demands.at.profit.max$weekly_demand[4]

fla.to.s35 <- 1522
fla.to.s51 <- 967
fla.to.s59 <- 2961
fla.to.s73 <- 1470

print('Weekly grove->storage cost: ')
0.22 * (s35.weekly.demand * fla.to.s35 +
        s51.weekly.demand * fla.to.s51 +
        s59.weekly.demand * fla.to.s59 +
        s73.weekly.demand * fla.to.s73)
print('Weekly revenue: ')
sum(fcoj.demands.at.profit.max$price *
    fcoj.demands.at.profit.max$weekly_demand * 2000)

print ('Annual grove->storage cost: ')
0.22 * (s35.weekly.demand * fla.to.s35 +
        s51.weekly.demand * fla.to.s51 +
        s59.weekly.demand * fla.to.s59 +
        s73.weekly.demand * fla.to.s73) * 48
print ('Annual futures purchase cost: ')
1.12847 * 136000 * 2000

print('Annual revenue: ')
sum(fcoj.demands.at.profit.max$price *
    fcoj.demands.at.profit.max$weekly_demand * 2000) * 48
