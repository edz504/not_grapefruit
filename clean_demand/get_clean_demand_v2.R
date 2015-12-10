
# S35
censored_week <- rep(0,48)
remove <- vector(mode="numeric", length=0)

while (i < 48) {
  i = 1
  censored = censored_week[i] + censored_week[i+1] + censored_week[i+2] + censored_week[i+3]
  if (censored > 0) {
    remove = c(remove,i)
  }
  i = i+4
}

demand = demand[-remove,]

#demand matrix: col1 = quantity, col2 = price

