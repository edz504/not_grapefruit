library(dplyr)
library(ggplot2)
library(reshape2)

# Note: ORA is inflated
cwd <- getwd()
setwd('..')
ora <- rbind(read.csv('clean_demand/ora_demand.csv'),
             read.csv('update_demand/ora_demand_2016.csv'))
poj <- rbind(read.csv('clean_demand/poj_demand.csv'),
             read.csv('update_demand/poj_demand_2016.csv'))
roj <- rbind(read.csv('clean_demand/roj_demand.csv'),
             read.csv('update_demand/roj_demand_2016.csv'))
fcoj <- rbind(read.csv('clean_demand/fcoj_demand.csv'),
             read.csv('update_demand/fcoj_demand_2016.csv'))
setwd(cwd)
products <- c('ORA', 'POJ', 'ROJ', 'FCOJ')
regions <- sapply(unique(ora$region), as.character)

coef.fit.df <- data.frame(matrix(0, 28, 4))
colnames(coef.fit.df) <- c('intercept', 'c1', 'region', 'product')

x <- 1
i <- 1
total.SSE <- 0
for (df in list(ora, poj, roj, fcoj)) {
    j <- 1
    for (region in regions) {
        fit.df <- data.frame(
            weekly.demand=df[df$region == region, ]$demand / 4,
            price=df[df$region == region, ]$price)
        fit.df <- fit.df[fit.df$weekly.demand > 0, ]
        model <- lm(fit.df$weekly.demand ~ I(fit.df$price ^ (-2)))
        fit.df$pred <- predict(model)
        coef.fit.df[x, ] <- c(model$coef, regions[j], products[i])
        ggplot(fit.df, aes(x=price)) + geom_point(aes(y=weekly.demand)) +
            geom_line(aes(y=pred), colour='#e74c3c')
        ggsave(file=paste(
            'demand_curves/fitted_demand_', regions[j], '_',
            products[i], '.png', sep=''),
               width=10, height=6)
        total.SSE <- total.SSE +
            sum((fit.df$pred - fit.df$weekly.demand)^2)
        j <- j + 1
        x <- x + 1
    }
    i <- i + 1
}
total.SSE

write.csv(coef.fit.df, 'demand_fit_coefs.csv',
          quote=FALSE, row.names=FALSE)
