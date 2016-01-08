The code here is used to optimize the balance between ROJ and POJ production in our second real round.  We have FCOJ coming in from futures and that should satisfy the demand around the country.  We are processing at half-capacity to maintain the 1:2 processing:tanker-user ratio, in order to avoid using carriers.  This means that we have the following processing constraints:

P02: 855 tons / week   (DS)
P03: 2730 tons / week  (SE, MA, NE)
P05: 885 tons / week   (SW, NW)
P09: 645 tons / week   (MW)

Then, we optimize the balance of ROJ and POJ to make in a given week, for a given plant.  For example, for P02:

max R * [p_R(R) - c_R(R)] + P * [p_P(P) - c_P(P)]
s.t. R + P = 855

where R and P are the amounts of ROJ and POJ manufactured, respectively.  We also know that c_R(R) = (650 + 1000) * R because we must first manufacture FCOJ and then reconstitute it, and c_P(R) = 2000 * R is simply the manufacturing cost of POJ.  We disregard storage and transportation costs, because those apply equally to both of the two products.  The p functions are the highest price we can sell a given quantity of product for and not over-estimate demand.

Results
=====
For P02 (region DS), objective maximization is at
R = 293 ($/lb = 1.71149262229), P = 562 ($/lb = 1.92597962063)
For P09 (region MW), objective maximization is at
R = 329 ($/lb = 1.97153817161), P = 316 ($/lb = 2.36047760922)
For P05 (regions SW, NW), objective maximization is at
R = 546 ($/lb = 1.5975975976), P = 339 ($/lb = 2.07507507508)
For P03 (regions NE, MA, SE), objective maximization is at
R = 1490 ($/lb = 1.78978978979), P = 1240 ($/lb = 2.11711711712)

Note that due to the method by which we aggregated demand over multiple regions (for a given storage system / processing plant), we don't have true price differentiation among those regions.