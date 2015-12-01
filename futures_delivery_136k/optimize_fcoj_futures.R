library(dplyr)
library(ggplot2)

cwd <- getwd()
setwd('..')
all.demands <- read.csv('fit_demand/all_predicted_demands.csv',
    stringsAsFactors=FALSE)
fcoj.demands <- all.demands[all.demands$product == 'FCOJ', ]

fcoj.demands$weekly_revenue <- fcoj.demands$price *
    fcoj.demands$predicted_demand * 2000
fla.to.s35 <- 1522
fla.to.s51 <- 967
fla.to.s59 <- 2961
fla.to.s73 <- 1470
fcoj.demands$fla.to.storage <- c(rep(fla.to.s51, 903),
                                 rep(fla.to.s73, 301),
                                 rep(fla.to.s35, 301),
                                 rep(fla.to.s59, 602))
fcoj.demands$fla.to.storage.cost <- 0.22 *
    fcoj.demands$predicted_demand *
    fcoj.demands$fla.to.storage
closest.storage.dists <- read.csv(
    'fit_demand/region_storage_dists_opt.csv')
fcoj.demands$storage.to.market <- c(rep(479.1429, 301),
                                    rep(286.7647, 301),
                                    rep(712.1667, 301),
                                    rep(368.5909, 301),
                                    rep(413.3750, 301),
                                    rep(659.1250, 301),
                                    rep(659, 301))
fcoj.demands$storage.to.market.cost <- 1.2 *
    fcoj.demands$predicted_demand *
    fcoj.demands$storage.to.market

fcoj.demands$profit <- fcoj.demands$weekly_revenue - (
    fcoj.demands$fla.to.storage.cost +
    fcoj.demands$storage.to.market.cost)

opt <- fcoj.demands %>%
    group_by(region) %>%
        filter(profit==max(profit)) %>%
            select(region, price,
                   predicted_demand, weekly_revenue,
                   profit)

print('Profit - purchase cost')
sum(opt$profit) - (1.12847 * 136000 * 2000 / 48)

# The above needs to be constrained by our demands, which
# need to sum to less than 2834.

# This function takes in a vector of prices
# (NE, MA, SE, MW, DS, NW, SW) and returns a dataframe
# with the relevant revenue and profit.
get.profits <- function(region.prices) {
    ind1 <- which(fcoj.demands$region == 'NE' &
                  fcoj.demands$price == region.prices[1])
    ind2 <- which(fcoj.demands$region == 'MA' &
                  fcoj.demands$price == region.prices[2])
    ind3 <- which(fcoj.demands$region == 'SE' &
                  fcoj.demands$price == region.prices[3])
    ind4 <- which(fcoj.demands$region == 'MW' &
                  fcoj.demands$price == region.prices[4])
    ind5 <- which(fcoj.demands$region == 'DS' &
                  fcoj.demands$price == region.prices[5])
    ind6 <- which(fcoj.demands$region == 'NW' &
                  fcoj.demands$price == region.prices[6])
    ind7 <- which(fcoj.demands$region == 'SW' &
                  fcoj.demands$price == region.prices[7])
    return(fcoj.demands[c(ind1, ind2, ind3, ind4, ind5, ind6, ind7),
                        c(1, 3, 4, 5, ncol(fcoj.demands))])
}

# Try optimal solution and increase the MW price and see
# if we meet the sum(predicted_demand) < 2834 constraint anywhere.
region.prices <- c(1, 1, 1.06, 1, 1, 1.41, 1.41)
p.vec <- unique(fcoj.demands$price)

subopt <- matrix(NA, length(p.vec), 3)
colnames(subopt) <- c('varied_price', 'profit', 'predicted_demand')
i <- 1
for (p in p.vec) {
    region.prices[4] <- p
    df <- get.profits(region.prices)
    subopt[i, ] <- c(p, sum(df$profit), sum(df$predicted_demand))
    i <- i + 1
}

region.prices <- c(1.5, 1.5, 1.5, 1.3, 1.25, 2.5, 2.5)
df <- get.profits(region.prices)
sum(df$profit)
sum(df$predicted_demand)

f <- function(region.prices) {
    df <- get.profits(region.prices)
    return(sum(df$profit))
}
g <- function(region.prices) {
    df <- get.profits(region.prices)
    return(sum(df$predicted_demand))
}

get.obj.const <- function(region.prices) {
    print(f(region.prices))
    print(g(region.prices))
}

# Plot profit as a function of price.  The steepness of curves
# should help us make a quantitative optimization.
setwd(cwd)  
ggplot(fcoj.demands, aes(x=price, y=profit, colour=region)) +
    geom_line() +
    ggtitle('FCOJ profit vs. price (no purchase cost)')
ggsave('FCOJ_profit_vs_price.png', width=10, height=6)
ggplot(fcoj.demands, aes(x=price, y=predicted_demand, colour=region)) +
    geom_line() +
    ggtitle('FCOJ weekly demand vs. price (no purchase cost)')
ggsave('FCOJ_weekly_demand_vs_price.png', width=10, height=6)

diffs <- fcoj.demands %>%
    group_by(region) %>%
        mutate(delD = c(0, diff(predicted_demand)),
               delP = c(0, diff(profit))) %>%
        select(region, price, predicted_demand,
               profit, delD, delP) %>%
        mutate(delPdelD = delP / delD) %>%
        na.omit()

ggplot(diffs, aes(x=price, y=delPdelD, colour=region)) +
    geom_line() +
    ggtitle('dP/dD over price')


# Best so far:
get.obj.const(c(1.5, 1.5, 1.53, 1.38, 1.4, 2.1, 2))

# [1] 6112246
# [1] 2836.821

prices <- c(1.5, 1.5, 1.53, 1.38, 1.4, 2.1, 2)
regions <- unique(fcoj.demands$region)

optimal.fcoj <- data.frame(
    matrix(NA, length(prices), ncol(fcoj.demands)))
colnames(optimal.fcoj) <- colnames(fcoj.demands)

for (i in 1:length(prices)) {
    optimal.fcoj[i, ] <- fcoj.demands[
        fcoj.demands$region == regions[i] &
        fcoj.demands$price == prices[i],]
}

write.csv(optimal.fcoj, 'optimal_fcoj_136k.csv',
          quote=FALSE, row.names=FALSE)