library(dplyr)
library(ggplot2)
library(reshape2)

# Note: ORA is inflated
cwd <- getwd()
setwd("/Users/Jessica/not_grapefruit/clean_demand")
data <- read.csv('MomPopAndNotGrapeFruit_Sales-Price-Region-Product-Year-Month-Source.csv')
ora <- subset(data,Product == "ORA")
poj <- subset(data,Product == "POJ")
roj <- subset(data,Product == "ROJ")
fcoj <- subset(data,Product == "FCOJ")
setwd("/Users/Jessica/not_grapefruit/")
products <- c('ORA', 'POJ', 'ROJ', 'FCOJ')
regions <- sapply(unique(ora$Region), as.character)

coef.fit.df <- data.frame(matrix(0, 28, 5))
colnames(coef.fit.df) <- c('intercept', 'c1', 'variance', 'region', 'product')

x <- 1
i <- 1
total.SSE <- 0
for (df in list(ora, poj, roj, fcoj)) {
    j <- 1
    for (region in regions) {
        fit.df <- data.frame(
            weekly.demand=df[df$Region == region, ]$Sales / 4,
            price=df[df$Region == region, ]$Price)
        fit.df <- fit.df[fit.df$weekly.demand > 0, ]
        model <- lm(fit.df$weekly.demand ~ I(fit.df$price ^ (-2)))
        fit.df$pred <- predict(model)
        ## remove outliers and fit model again
        fit.df <- subset(fit.df,abs(fit.df$weekly.demand-fit.df$pred)<100)
        model <- lm(fit.df$weekly.demand ~ I(fit.df$price ^ (-2)))
        fit.df$pred <- predict(model)
        coef.fit.df[x, ] <- c(model$coef, sum((fit.df$pred - fit.df$weekly.demand)^2)/(length(fit.df$pred)-1),regions[j], products[i])
        #ggplot(fit.df, aes(x=price)) + geom_point(aes(y=weekly.demand)) +
            #geom_line(aes(y=pred), colour='#e74c3c')
        #ggsave(file=paste(
            #'fitted_demand_', regions[j], '_',
            #products[i], '.png', sep=''),
               #width=10, height=6)
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
