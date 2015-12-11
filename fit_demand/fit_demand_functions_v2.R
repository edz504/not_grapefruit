library(dplyr)
library(ggplot2)
library(reshape2)

# Note: ORA is inflated
cwd <- getwd()
setwd("/Users/Jessica/not_grapefruit/clean_demand")
data <- read.csv('MomPopAndNotGrapeFruit_Sales-Price-Region-Product-Year-Month-Source.csv')
#setwd("/Users/Jessica/not_grapefruit/fit_demand")
#data1 <- read.csv('MomPop_NotGrapefruit_withIndicator0.csv')
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
        #fit.df <- subset(fit.df,abs(fit.df$weekly.demand-fit.df$pred)<100)
        #model <- lm(fit.df$weekly.demand ~ I(fit.df$price ^ (-2)))
        #fit.df$pred <- predict(model)
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

write.csv(coef.fit.df, 'demand_fit_coefs_clean.csv',
          quote=FALSE, row.names=FALSE)

# checking if removing outlier or removing censored demand works better
# removing outlier seems to work better 
check = coef.fit.df <- data.frame(matrix(0, 1000, 4))
total.SSE=0
tatal.SSE1=0
setwd("/Users/Jessica/not_grapefruit/fit_demand")
coef <- read.csv('demand_fit_coefs_outlier.csv')
setwd("/Users/Jessica/not_grapefruit/fit_demand")
coef1 <- read.csv('demand_fit_coefs_clean.csv')
for (product in products) {
  for (region in regions) {
    a <- subset(coef$c1, coef$region == region & coef$product == product)
    b <- subset(coef$intercept, coef$region == region & coef$product == product)
    price <- subset(data1$Price,coef$region == region & coef$product == product)
    demand <- subset(data1$Sales,coef$region == region & coef$product == product)/4
    demand = subset(demand, demand>0)
    #outlier removed
    predict <- a/price^2 + b
    a1 <- subset(coef1$c1, coef$region == region & coef$product == product)
    b1 <- subset(coef1$intercept, coef$region == region & coef$product == product)
    #clean (removing all censored)
    predict1 <- a1/price^2 + b1
    total.SSE = total.SSE + sum((predict - demand)^2)
    total.SSE1 = total.SSE + sum((predict1 - demand)^2)
  }
}
total.SSE #removing outliers 165814565
total.SSE1 #removing censored demand 168710178



