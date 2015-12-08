library(dplyr)

coefs <- read.csv('demand_fit_coefs.csv',
                  stringsAsFactors=FALSE)

# p = sqrt(a / (D - b))


##### MW
# Want to sell 301 of ORA at MW.  Priced at $2.35 creates
# ~200 - 300 demand (not enough).
this.coefs <- coefs %>%
    filter(region == 'MW' & product == 'ORA') %>%
    select(intercept, c1)
sqrt(this.coefs$c1 / (301 - this.coefs$intercept))
# $2.12

quantity <- (this.coefs$c1 / 2.35 ^ 2 + this.coefs$intercept)
prev.profit <- 2.35 *
    quantity +
    60 * (301 - quantity) +
    


# Want to sell 110 of POJ at MW.  Priced at $4.00 creates
# ~100 demand (not enough).
this.coefs <- coefs %>%
    filter(region == 'MW' & product == 'POJ') %>%
    select(intercept, c1)
sqrt(this.coefs$c1 / (110 - this.coefs$intercept))
# $3.85

# Want to sell 80 of ROJ at MW. Priced at $3.90 creates
# 60-80 demand (not enough)
# Don't change -- FCOJ will fix.


# Want to sell 675 of FCOJ at MW.  Priced at $1.48 creates
# ~500 - 700 demand (not enough).
this.coefs <- coefs %>%
    filter(region == 'MW' & product == 'FCOJ') %>%
    select(intercept, c1)
sqrt(this.coefs$c1 / (700 - this.coefs$intercept))
# bad output -- try $1.30

#### SW, NW
# Want to sell 132 ORA at SW, NW together.  Priced at $4 (NW)
# and $2.75 (SW) didn't sell enough.
sw.coefs <- coefs %>%
    filter(region == 'SW' & product == 'ORA') %>%
    select(intercept, c1)
nw.coefs <- coefs %>%
    filter(region == 'NW' & product == 'ORA') %>%
    select(intercept, c1)

p.vec <- seq(1, 4, by=0.01)
i <- 1
max.rev <- -Inf
p.sw.max <- -1
p.nw.max <- -1
for (p.sw in p.vec) {
    for (p.nw in p.vec) {
        d1 <- sw.coefs$c1 / p.sw ^ 2 + sw.coefs$intercept
        d2 <- nw.coefs$c1 / p.nw ^ 2 + nw.coefs$intercept
        if (abs(d1 + d2 - 132) < 5) {
            this.rev <- d1 * p.sw + d2 * p.nw
            if (this.rev > max.rev) {
                max.rev <- this.rev
                p.sw.max <- p.sw
                p.nw.max <- p.nw
            }
        }
    }
}
# $2.63 (NW) and $3.15 (SW)


# Want to sell 284 POJ at SW, NW together.  Priced at $4 (NW)
# and $4 (SW) didn't sell enough.
sw.coefs <- coefs %>%
    filter(region == 'SW' & product == 'POJ') %>%
    select(intercept, c1)
nw.coefs <- coefs %>%
    filter(region == 'NW' & product == 'POJ') %>%
    select(intercept, c1)

p.vec <- seq(1, 4, by=0.01)
i <- 1
max.rev <- -Inf
p.sw.max <- -1
p.nw.max <- -1
for (p.sw in p.vec) {
    for (p.nw in p.vec) {
        d1 <- sw.coefs$c1 / p.sw ^ 2 + sw.coefs$intercept
        d2 <- nw.coefs$c1 / p.nw ^ 2 + nw.coefs$intercept
        if (abs(d1 + d2 - 284) < 5) {
            this.rev <- d1 * p.sw + d2 * p.nw
            if (this.rev > max.rev) {
                max.rev <- this.rev
                p.sw.max <- p.sw
                p.nw.max <- p.nw
            }
        }
    }
}
# $2.25 (NW) and $2.26 (SW)

## ROJ: unchanged (FCOJ fix will fix this)
## FCOJ: $2.10 (NW) and $2.00 (SW)

#########
# Want to sell 857 ORA at NE, MA, SE together.  Priced at
# $2.10 (NE), $2 (MA), and $2.30 (SE) didn't sell enough.
se.coefs <- coefs %>%
    filter(region == 'SE' & product == 'ORA') %>%
    select(intercept, c1)
ne.coefs <- coefs %>%
    filter(region == 'NE' & product == 'ORA') %>%
    select(intercept, c1)
ma.coefs <- coefs %>%
    filter(region == 'MA' & product == 'ORA') %>%
    select(intercept, c1)

p.vec <- seq(1, 4, by=0.05)
i <- 1
max.rev <- -Inf
p.se.max <- -1
p.ne.max <- -1
p.ma.max <- -1
for (p.se in p.vec) {
    for (p.ne in p.vec) {
        for (p.ma in p.vec) {
            d1 <- se.coefs$c1 / p.se ^ 2 + se.coefs$intercept
            d2 <- ne.coefs$c1 / p.ne ^ 2 + ne.coefs$intercept
            d3 <- ma.coefs$c1 / p.ma ^ 2 + ma.coefs$intercept
            if (abs(d1 + d2 + d3 - 857) < 5) {
                this.rev <- d1 * p.se + d2 * p.ne + d3 * p.ma
                if (this.rev > max.rev) {
                    max.rev <- this.rev
                    p.se.max <- p.se
                    p.ne.max <- p.ne
                    p.ma.max <- p.ma
                }
            }
        }
    }
}
# $2.05 (NE), $1.95 (MA), $1.85 (SE)


# Want to sell 385 POJ at NE, MA, SE together.  Priced at
# $3.43 (NE), $3.38 (MA), and $4.00 (SE) didn't sell enough.
se.coefs <- coefs %>%
    filter(region == 'SE' & product == 'POJ') %>%
    select(intercept, c1)
ne.coefs <- coefs %>%
    filter(region == 'NE' & product == 'POJ') %>%
    select(intercept, c1)
ma.coefs <- coefs %>%
    filter(region == 'MA' & product == 'POJ') %>%
    select(intercept, c1)

p.vec <- seq(1, 4, by=0.05)
i <- 1
max.rev <- -Inf
p.se.max <- -1
p.ne.max <- -1
p.ma.max <- -1
for (p.se in p.vec) {
    for (p.ne in p.vec) {
        for (p.ma in p.vec) {
            d1 <- se.coefs$c1 / p.se ^ 2 + se.coefs$intercept
            d2 <- ne.coefs$c1 / p.ne ^ 2 + ne.coefs$intercept
            d3 <- ma.coefs$c1 / p.ma ^ 2 + ma.coefs$intercept
            if (abs(d1 + d2 + d3 - 857) < 5) {
                this.rev <- d1 * p.se + d2 * p.ne + d3 * p.ma
                if (this.rev > max.rev) {
                    max.rev <- this.rev
                    p.se.max <- p.se
                    p.ne.max <- p.ne
                    p.ma.max <- p.ma
                }
            }
        }
    }
}
# $2.50 (NE), $2.45 (MA), $2.65 (SE)

## ROJ: $3.55 (NE), $3.56 (MA), $3.85 (SE)
## FCOJ: $1.65 (NE), $1.65 (MA), $1.70 (SE).


#### DS
# ORA: $2.25
# POJ: $3.45
# ROJ: $4.00
# FCOJ: $2.00