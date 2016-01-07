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
write.csv(demand.curves.df, file='all_predicted_demands.csv',
          quote=FALSE, row.names=FALSE)