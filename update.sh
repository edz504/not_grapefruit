#!/bin/sh
cd "demand_pipeline"
# python CollectSalesDataAcrossYears.py
Rscript demand_fit_plot.R 0
Rscript create_demand_table.R
Rscript find_optimal_prices_ORA_POJ_ROJ.R
Rscript find_optimal_prices_FCOJ_constrained.R 500000 136000 48 0.961788527
Rscript find_optimal_prices_FCOJ_ROJ.R 0.961788527
