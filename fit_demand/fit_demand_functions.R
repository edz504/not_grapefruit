library(dplyr)
library(ggplot2)
library(reshape2)

# Note: ORA is inflated
ora <- read.csv('ora_demand_opt.csv')
poj <- read.csv('poj_demand_opt.csv')
roj <- read.csv('roj_demand_opt.csv')
fcoj <- read.csv('fcoj_demand_opt.csv')
products <- c('ORA', 'POJ', 'ROJ', 'FCOJ')
regions <- sapply(unique(ora$region), as.character)

weekly.demand <- poj[poj$region == 'NE', ]$weekly_demand
price <- poj[poj$region == 'NE', ]$price

coef.fit.df <- data.frame(matrix(0, 28, 4))
colnames(coef.fit.df) <- c('intercept', 'c1', 'region', 'product')

x <- 1
i <- 1
for (df in list(ora, poj, roj, fcoj)) {
    j <- 1
    for (region in regions) {
        fit.df <- data.frame(
            weekly.demand=df[df$region == region, ]$weekly_demand,
            price=df[df$region == region, ]$price)
        fit.df <- fit.df[fit.df$weekly.demand > 0, ]
        model <- lm(fit.df$weekly.demand ~ I(fit.df$price ^ (-2)))
        coef.fit.df[x, ] <- c(model$coef, regions[j], products[i])
        j <- j + 1
        x <- x + 1
    }
    i <- i + 1
}

write.csv(coef.fit.df, 'demand_fit_coefs.csv',
          quote=FALSE, row.names=FALSE)
