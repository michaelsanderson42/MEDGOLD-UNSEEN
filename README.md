# MEDGOLD-UNSEEN
Code for study of extreme rainfall in northern Portugal, focusing on vineyards

Procedure for regridding Iberia01 data to DePreSys3 grid.
For some reason, the left-hand column and upper row are returned as
missing data by iris.cube.regrid.
Instead, had to use cdo remapcon (1st order conservative, uses area-weighting).

1. Load Iberia01 data into an Iris cube. Set mask to False. Set all masked values
   to zero. Save the modified cube
2. Regrid the modified Iberia01 data:
   cdo remapcon,DePreSys3_pr_iberia_annual_ensmean.nc ibera01_mdizero.nc ./tmp/iberia01_v1.0_pr_iberia_annual_mean.nc
3. Read in the regridded Iberia01 data, set all data points equal to zero to masked values
4. Save the Iberia01 data as a cube

Step 1: Python program prepare_iberia01_data.py
Step 2: Linux script regrid.sh
Steps 3-4: Python program finish_iberia01_data.py
