The code here is used to optimize the balance between ROJ and POJ production in our second real round.  We have FCOJ coming in from futures and that should satisfy the demand around the country.  We are processing at half-capacity to maintain the 1:2 processing:tanker-user ratio, in order to avoid using carriers.  This means that we have the following processing constraints:

P02: 855 tons / week   (DS)
P03: 2730 tons / week  (SE, MA, NE)
P05: 885 tons / week   (SW, NW)
P09: 645 tons / week   (MW)

Then, we optimize the balance of ROJ and POJ to make in a given week, for a given plant.  For example, for P02:

max R * [p_R(R) - c_R(R)] + P * [p_P(P) - c_P(P)]
s.t. R + P = 855

where R and P are the amounts of ROJ and POJ manufactured, respectively.  We also know that c_R(R) = (650 + 1000) * R because we must first manufacture FCOJ and then reconstitute it, and c_P(R) = 2000 * R is simply the manufacturing cost of POJ.  We disregard storage and transportation costs, because those apply equally to both of the two products.  The p functions are the highest price we can sell a given quantity of product for and not over-estimate demand.

I think we need to re-fit the functions to have a sharper rise, which might be more realistic, possibly y = 1 / x^2