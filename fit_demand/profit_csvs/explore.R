library(dplyr)

fcoj <- read.csv('fcoj_max_profit.csv', stringsAsFactors=FALSE)
ora <- read.csv('ora_max_profit.csv', stringsAsFactors=FALSE)
poj <- read.csv('poj_max_profit.csv', stringsAsFactors=FALSE)
roj <- read.csv('roj_max_profit.csv', stringsAsFactors=FALSE)

df <- rbind(fcoj[, c(1:5, ncol(fcoj))],
            ora[, c(1:5, ncol(ora))],
            poj[, c(1:5, ncol(poj))],
            roj[, c(1:5, ncol(roj))])

profit <- sum(df$profit) * 48 - (4 * 7500000 + 4 * 8000000)