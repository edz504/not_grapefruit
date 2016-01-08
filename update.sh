#!/bin/sh
cd "demand_pipeline"
echo "Collecting new sales data..."
python CollectSalesDataAcrossNewYear.py 2019
echo "Updating demand curves..."
Rscript demand_fit_plot.R 0
echo "Updating grove beliefs..."
python update_beliefs.py 2019
echo "Creating demand tables..."
Rscript create_demand_table.R
echo "Optimizing ORA, POJ profits..."
Rscript find_optimal_prices_ORA_POJ.R
echo "Optimizing FCOJ, ROJ futures profits..."
Rscript find_optimal_prices_FCOJ_ROJ.R 0.961788527 # CHANGE THIS
echo "Adjusting FCOJ, ROJ prices..."
Rscript adjust_optimal_to_constraint_FCOJ_ROJ.R
echo "Writing initial decisions..."
python calculate_and_write_decisions.py