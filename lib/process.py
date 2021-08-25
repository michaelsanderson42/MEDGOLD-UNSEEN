import os
import glob
import iris
import iris.coord_categorisation


UDIR = '/data/users/hadmi/MED-GOLD/UNSEEN/native_grids'


def process_chirps(var_name, year_range, lon_lim, lat_lim, version, region_name, season):
    '''
    Reads in CHIRPS gridded rainfall data.
    Extracts the data for the given region and time period.
    Regrids the data to the resolution of DePreSys3.

    var_name -- Name of variable, e.g., 'pr'
    year_range -- 2-element list containing the first and last years to be processed.
    lon_lim, lat_lim -- 2-element lists containing edges of region required
    version -- The version of the CHIRPS data, e.g., '2.0'
    region_name -- Name of the region, 'douro' or 'iberia'
    season -- The season name, e.g., 'amj', 'annual'
    '''

# The CHIRPS data are stored in this directory. There is 1 file per year for 1981-2015
    indir = '/project/earthobs/PRECIPITATION/CHIRPS/'

# Set up constraints for the Iberian Peninsula, expanded as data will be regridded to a coarser resolution.
    delta = 2.0
    lon_con = iris.Constraint(longitude = lambda l: lon_lim[0]-delta <= l <= lon_lim[1]+delta)
    lat_con = iris.Constraint(latitude = lambda l: lat_lim[0]-delta <= l <= lat_lim[1]+delta)
    all_con = lon_con & lat_con

    clist = iris.cube.CubeList()

# Load in the CHIRPS data for the given region and time period.
    for the_year in list(range(year_range[0], year_range[1]+1)):
# CHIRPS data officially end in 2015; data for 2016 are incomplete.
        if the_year > 2015:
            break
        filename = f'chirps-v{version}.{the_year:4d}.days_p25.nc'
        try:
# Load the CHIRPS data, one year at a time.
            chirps_daily = iris.load_cube(os.path.join(indir, filename), all_con)
# Remove history in global attributes, as is stopping cube concatenation.
            chirps_daily.attributes = {}
# CHIRPS rainfall have units of mm day-1. Change the unit description to be CF-compliant.
            if var_name == 'pr':
                chirps_daily.standard_name = 'precipitation_amount'
                chirps_daily.units = 'kg m-2 day-1'

            if season == 'annual':
# Calculate annual total rainfall
                chirps_annual = chirps_daily.collapsed('time', iris.analysis.SUM)
                clist.append(chirps_annual)
            else:
# Calculate seasonal total rainfall
                all_months = 'jfmamjjasond'
                i = all_months.index(season)
                nmths = len(season)
                vine_seasons = [all_months[:i], all_months[i:i+nmths], all_months[i+nmths:]]

# Add the seasons and year as coordinates
# if seasons straddle the year boundaries, need to use 'season_year' instead
                iris.coord_categorisation.add_year(chirps_daily, 'time', name='year')
                iris.coord_categorisation.add_season(chirps_daily, 'time', name='season', seasons=vine_seasons)
                chirps_season = chirps_daily.aggregated_by(['season', 'year'], iris.analysis.SUM).extract(iris.Constraint(season = season))
                clist.append(chirps_season)
            
        except:
            pass

# Create a single cube containing a series of annual or seasonal totals on the native CHIRPS grid.
    chirps_series = clist.merge_cube()

# Add bounds to the coordinates of the CHIRPS data, if not present.
    if not chirps_series.coord('longitude').has_bounds():
        chirps_series.coord('longitude').guess_bounds()
    if not chirps_series.coord('latitude').has_bounds():
        chirps_series.coord('latitude').guess_bounds()

# Save the CHIRPS time series
    filename = f'chirps_v{version}_{var_name}_{region_name}_{season}_series.nc'
    iris.save(chirps_series, os.path.join(UDIR, filename))

# Calculate average of annual or seasonal totals
    cube = chirps_series.collapsed('time', iris.analysis.MEAN)

# Add bounds to the coordinates of the CHIRPS data, if not present.
    if not cube.coord('longitude').has_bounds():
        cube.coord('longitude').guess_bounds()
    if not cube.coord('latitude').has_bounds():
        cube.coord('latitude').guess_bounds()

# Save the averaged CHIRPS data
    filename = f'chirps_v{version}_{var_name}_{region_name}_{season}_mean.nc'
    iris.save(cube, os.path.join(UDIR, filename))
