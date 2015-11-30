library(ggplot2)

demands.df <- read.csv('demand_fit_coefs.csv',
    stringsAsFactors = FALSE)
p.vec <- seq(1, 4, by=0.01)

demand.curves.df <- data.frame(
    matrix(NA, length(p.vec) * nrow(demands.df), 4))
colnames(demand.curves.df) <- c('region', 'product', 'price',
                                'predicted_demand')

x <- 1
for (i in 1:nrow(demands.df)) {
    vals <- demands.df[i, ]
    for (p in p.vec) {
        demand <- vals[2] / (p ^ 2) + vals[1]
        demand.curves.df[x, ] <- c(vals[3], vals[4], p, demand)
        x <- x + 1
    }
}

demand.curves.df$region <- factor(demand.curves.df$region)
demand.curves.df$product <- factor(demand.curves.df$product)

ggplot(demand.curves.df, aes(x=price, y=predicted_demand)) +
    geom_line(aes(colour=region)) + facet_wrap(~ product, ncol=2) +
    ggtitle('Weekly Demands (fitted) by Product and Region')
ggsave('fitted_weekly_demands_p_r.png', width=10, height=6)

ggplot(demand.curves.df, aes(x=price, y=predicted_demand)) +
    geom_line(aes(colour=product)) + facet_wrap(~ region, ncol=2) +
    ggtitle('Weekly Demands (fitted) by Region and Product')
ggsave('fitted_weekly_demands_r_p.png', width=10, height=6)