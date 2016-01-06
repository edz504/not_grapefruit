library(dplyr)
library(ggplot2)

# Visualize option
args <- commandArgs(trailingOnly = TRUE)
PLOT_AND_SAVE <- as.integer(args[1])

sales_df <- read.csv('sales.csv', stringsAsFactors=FALSE)
sales_df$weekly_sales <- sales_df$Sales / 4
regions <- unique(sales_df$Region)
products <- unique(sales_df$Product)
price_neighborhoods <- seq(1, 4, by=0.75)

get.neighborhood <- function(p, price_neighborhoods) {
    # Take care of tail end
    if (p == 4) {
        return(length(price_neighborhoods) - 1)
    }
    # Note we take the last element because neighborhoods
    # are inclusive on the lower end.
    found <- which(sort(c(p, price_neighborhoods)) == p)
    return(found[length(found)] - 1)
}

# Testing get.neighborhood
# for (p in seq(1, 4, by=0.1)) {
#     print(p)
#     print(get.neighborhood(p, price_neighborhoods))
# }

PROP = 0.25

coef_fit_df <- data.frame(matrix(0, 28, 4))
colnames(coef_fit_df) <- c('b',
                           'a',
                           'region',
                           'product')
j <- 1
for (region in regions) {
    for (product in products) {
        this_df <- sales_df %>%
            filter(Region == region, Product == product) %>%
            filter(weekly_sales > 0) # This isn't removing censored
            # data, it's just removing point with no sales.

        # Apply neighborhood-based removal of censored data.
        # First, we find the max value in each neighborhood
        # [1, 1.5), [1.5, 2), ...
        neighborhood_maxes <- rep(NA,
            length(price_neighborhoods) - 1)
        for (i in 1:length(neighborhood_maxes)) {
            p_lower <- price_neighborhoods[i]
            p_upper <- price_neighborhoods[i + 1]
            tmp <- this_df %>%
                filter(p_lower <= Price, Price < p_upper)
            neighborhood_maxes[i] <- max(tmp$weekly_sales)
        }

        # Then, we attach this max to each data point, and
        # remove the ones that are not within 50% of their
        # max (arbitrary number, should work well).
        this_df$local_max <- neighborhood_maxes[unlist(
            sapply(this_df$Price, FUN=get.neighborhood,
                   price_neighborhoods))]

        this_df$keep <- (
            this_df$weekly_sales > this_df$local_max * (1 - PROP) &
            this_df$weekly_sales < this_df$local_max * (1 + PROP))

        # Let's keep everything past price 3, though, because
        # censoring at that level is ineffective anyways.
        this_df[which(this_df$Price >= 3), ]$keep <- TRUE
        
        # Fit the model only on clean data
        clean_df <- this_df[this_df$keep, ]
        model <- lm(weekly_sales ~ I(Price ^ (-2)), data=clean_df)
        
        # Save the coefficients
        coef_fit_df[j, ] <- c(model$coef, region, product)
        j <- j + 1

        if (PLOT_AND_SAVE) {
            # Predict and plot on all prices.
            this_df$pred <- predict(model, this_df)
            ggplot(this_df, aes(x=Price)) +
                geom_point(aes(y=weekly_sales, colour=keep)) +
                geom_line(aes(y=pred))
            ggsave(paste('sales_and_fits_plots/', product, '_',
                          region, '.png', sep=''),
                   width=10, height=6)
        }
    }
}

write.csv(coef_fit_df, 'demand_fit_coefs.csv',
          quote=FALSE, row.names=FALSE)



