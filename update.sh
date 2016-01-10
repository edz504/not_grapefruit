#!/bin/sh
cd "demand_pipeline"
echo "Collecting new sales data..."
python CollectSalesDataAcrossNewYear.py 2019

echo "Updating demand curves..."
Rscript demand_fit_plot.R 0

# echo "Updating grove beliefs..."
# cd "../grove_beliefs"
# python update_beliefs.py 2018

echo "Creating demand tables..."
cd "../demand_pipeline"
Rscript create_demand_table.R

echo "Optimizing ORA, POJ profits..."
Rscript find_optimal_prices_ORA_POJ.R

echo "Optimizing FCOJ, ROJ futures profits..."
Rscript find_optimal_prices_FCOJ_ROJ.R 0.894719309 # Current 5-year price

echo "Adjusting FCOJ, ROJ prices..."
Rscript adjust_optimal_to_constraint_FCOJ_ROJ.R 0.95103434 136000 # Paid price and quantity

echo "Writing initial decisions..."
python calculate_and_write_decisions.py 2020