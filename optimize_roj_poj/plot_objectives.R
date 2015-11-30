library(ggplot2)

p02 <- read.csv('p02_optimization.csv')
ggplot(p02, aes(x=R, y=obj)) + geom_line()

p09 <- read.csv('p09_optimization.csv')
ggplot(p09, aes(x=R, y=obj)) + geom_line()

p05 <- read.csv('p05_optimization.csv')
ggplot(p05, aes(x=R, y=obj)) + geom_line()

p03 <- read.csv('p03_optimization.csv')
ggplot(p03, aes(x=R, y=obj)) + geom_line()