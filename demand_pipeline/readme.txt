This folder contains the code for updating the demand curves.  It uses VBA to create a csv from all past data (MomPop, Practice Rounds, and real rounds) with realized sales for a given price, product, and region.  It also provides a boolean indicating whether or not the sales represent censored demand (0 means clean).   

After the VBA script has been run, two methods have been used to fit demand curves.  In one method, we filter out all sale data that is censored, and then fit a separate model for each product and region.  In the other, we consider all data, but use a local / neighborhood max-based filtering method to filter out possibly censored data.  Both methods use the following model structure for each curve:

D(p) = a / (p ^ 2) + b

Notes to Jessica and John:
- Does the VBA produce the indicator data frame?  We'll want that regardless of which method we use
- We don't take into account inflation (when one product is getting spillover demand from the lack of of presence of other products)