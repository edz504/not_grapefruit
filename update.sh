#!/bin/sh
cd "demand_pipeline"
echo "Collecting new sales data..."
# python CollectSalesDataAcrossYears.py
echo "Updating demand curves..."
Rscript demand_fit_plot.R 0
echo "Creating demand tables..."
Rscript create_demand_table.R
echo "Optimizing ORA, POJ profits..."
Rscript find_optimal_prices_ORA_POJ.R
echo "Optimizing FCOJ, ROJ futures profits..."
Rscript find_optimal_prices_FCOJ_ROJ.R 0.961788527
# ^ fix that
echo "Adjusting FCOJ, ROJ prices..."
Rscript adjust_optimal_to_constraint_FCOJ_ROJ.R
# Note: must copy new decisions here with _init prefix
echo "Writing initial decisions..."
python calculate_and_write_decisions.py
# Make this pause while we copy above file with no _init prefix
echo "Adding price adjustments (betas)..."
python adjust_prices.py
echo "Updating beta beliefs..."
python update_pricing_adjustments.py