#!/bin/sh
cd "demand_pipeline"
echo "Adding price adjustments (betas)..."
python adjust_prices.py
echo "Updating beta beliefs..."
python update_pricing_adjustments.py