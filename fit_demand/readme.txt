The code here takes the raw weekly demands of each product, broken down by region, and fits it to the varying prices.  The model used is

demand = (a / (price ^ 2)) + b

The demand curves fitted here are also used in the optimize_roj_poj code.