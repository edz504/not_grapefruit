df <- c(
    read.csv('ora_max_profit.csv')$profit,
    read.csv('poj_max_profit.csv')$profit,
    read.csv('roj_max_profit.csv')$profit,
    read.csv('fcoj_fixed_quantity.csv')$profit)
# Change FCOJ and ROJ once we switch over.

fcoj.futures.price <- 0.95103434
fcoj.futures.quantity <- 136000

sum(df) * 48 -
    (fcoj.futures.price * fcoj.futures.quantity * 2000) -
    (4 * 7500000 + 4 * 8000000)

# 281,920,851