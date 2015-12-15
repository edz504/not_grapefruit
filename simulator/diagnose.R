library(ggplot2)
library(dplyr)

leftovers <- read.csv('leftovers.csv')
shortage <- read.csv('throwouts.csv')

plot <- leftovers %>%
    right_join(shortage, by=c('t', 'storage'))

# Shortage = inventory - capacity
# positive means we threw out
ggplot(plot, aes(x=t)) +
    geom_line(aes(y=leftover, colour=product)) +
    geom_line(aes(y=throwout)) +
    facet_wrap(~ storage, ncol=2)
ggsave('diagnose.png', width=10, height=6)