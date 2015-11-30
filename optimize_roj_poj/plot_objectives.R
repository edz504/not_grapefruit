library(ggplot2)

p02 <- read.csv('p02_optimization.csv')
ggplot(p02, aes(x=R, y=obj)) + geom_line()

p09 <- read.csv('p09_optimization.csv')
ggplot(p09, aes(x=R, y=obj)) + geom_line()