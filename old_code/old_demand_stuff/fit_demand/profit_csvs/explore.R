library(dplyr)

fcoj <- read.csv('fcoj_max_profit.csv', stringsAsFactors=FALSE)
ora <- read.csv('ora_max_profit.csv', stringsAsFactors=FALSE)
poj <- read.csv('poj_max_profit.csv', stringsAsFactors=FALSE)
roj <- read.csv('roj_max_profit.csv', stringsAsFactors=FALSE)

df <- rbind(ora[, c(1:5, ncol(ora))],
            poj[, c(1:5, ncol(poj))],
            roj[, c(1:5, ncol(roj))])

# Total profit, using FCOJ futures
for (fcoj_future_price in seq(0.6, 1.1, 0.1)) {
    profit <- 48 * sum(df$profit) +
        (6112246 * 48 - fcoj_future_price * 136000 * 2000) -
        (4 * 7500000 + 4 * 8000000)
    print(profit)
}

s51.no.fcoj <- df %>% filter(region %in% c('NE', 'MA', 'SE'))
sum(s51.no.fcoj$predicted_demand)
s35.no.fcoj <- df %>% filter(region %in% c('DS'))
sum(s35.no.fcoj$predicted_demand)
s73.no.fcoj <- df %>% filter(region %in% c('MW'))
sum(s73.no.fcoj$predicted_demand)
s59.no.fcoj <- df %>% filter(region %in% c('SW', 'NW'))
sum(s59.no.fcoj$predicted_demand)