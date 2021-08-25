import os
import glob
import iris
import iris.coord_categorisation


UDIR = '/data/users/hadmi/MED-GOLD/UNSEEN/native_grids'


def process_chirps(var_name, year_range, lon_lim, lat_lim, version, region_name, season):
    '''
    Reads in CHIRPS gridded rainfall data.
    Extracts the data for the given region and time period.
    Writes out the series and averaged data for the given region.

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
    chirps_series_mean = chirps_series.collapsed('time', iris.analysis.MEAN)

# Add bounds to the coordinates of the CHIRPS data, if not present.
    if not chirps_series_mean.coord('longitude').has_bounds():
        chirps_series_mean.coord('longitude').guess_bounds()
    if not chirps_series_mean.coord('latitude').has_bounds():
        chirps_series_mean.coord('latitude').guess_bounds()

# Save the averaged CHIRPS data
    filename = f'chirps_v{version}_{var_name}_{region_name}_{season}_mean.nc'
    iris.save(chirps_series_mean, os.path.join(UDIR, filename))


def process_eobs(var_name, year_range, lon_lim, lat_lim, version, region_name, season):
    '''
    Reads in E-OBS gridded rainfall data.
    Extracts the data for the given region and time period.
    Writes out the series and averaged data for the given region.

    var_name -- Name of variable, e.g., 'pr'
    year_range -- 2-element list containing the first and last years to be processed.
    lon_lim, lat_lim -- 2-element lists containing edges of region required
    version -- The version of the CHIRPS data, e.g., '2.0'
    region_name -- Name of the region, 'douro' or 'iberia'
    season -- The season name, e.g., 'amj', 'annual'
    '''

# Set up constraints for the Iberian Peninsula, expanded as data will be regridded to a coarser resolution.
    delta = 2.0
    lon_con = iris.Constraint(longitude = lambda l: lon_lim[0]-delta <= l <= lon_lim[1]+delta)
    lat_con = iris.Constraint(latitude = lambda l: lat_lim[0]-delta <= l <= lat_lim[1]+delta)

# Set up a time constraint
    time_con = iris.Constraint(time=lambda cell: year_range[0] <= cell.point.year <= year_range[1])
    all_con = time_con & lon_con & lat_con

    eobs_daily = load_eobs_v20_onwards(var_name, version, all_con)

    if season == 'annual':
# Calculate annual total rainfall
        iris.coord_categorisation.add_year(eobs_daily, 'time', name='year')
        eobs_series = eobs_daily.aggregated_by('year', iris.analysis.SUM)

    else:
# Calculate seasonal total rainfall amounts
        all_months = 'jfmamjjasond'
        i = all_months.index(season)
        nmths = len(season)
        vine_seasons = [all_months[:i], all_months[i:i+nmths], all_months[i+nmths:]]

# Add the seasons and year as coordinates
# if seasons straddle the year boundaries, need to use 'season_year' instead
        iris.coord_categorisation.add_season(eobs_daily, 'time', name='season', seasons=vine_seasons)
        iris.coord_categorisation.add_year(eobs_daily, 'time', name='year')
        eobs_series = eobs_daily.aggregated_by(['season', 'year'], iris.analysis.SUM).extract(iris.Constraint(season = season))

# Add bounds to the coordinates of the E-OBS data, if needed.
    if not eobs_series.coord('longitude').has_bounds():
        eobs_series.coord('longitude').guess_bounds()
    if not eobs_series.coord('latitude').has_bounds():
        eobs_series.coord('latitude').guess_bounds()

# Save the E-OBS time series
    filename = f'eobs_v{version}_{var_name}_{region_name}_{season}_series.nc'
    iris.save(eobs_series, os.path.join(UDIR, filename))

# Average of annual or seasonal totals
    eobs_series_mean = eobs_series.collapsed('time', iris.analysis.MEAN)

# Save the averaged data
    filename = f'eobs_v{version}_{var_name}_{region_name}_{season}_mean.nc'
    iris.save(eobs_series_mean, os.path.join(UDIR, filename))


def load_eobs_v20_onwards(var_name, version, all_con):
    '''
    Reads in EOBS data, for versions 20 onwards

    var_name -- variable name
    version --  E-OBS version to read in
    all_con -- Combination of time and spatial constraints

    Returns:
       Iris cube containing E-OBS data for the times and area specified.
    '''

    if var_name == 'pr':
        var = 'rr'

    eobs_path = '/project/earthobs/EOBS/v{}/'.format(version)
    eobs_file_header = f'{var}_ens_mean_0.1deg_reg_*_v{version}.0e.nc'
    eobs_filenames = glob.glob(os.path.join(eobs_path, eobs_file_header))
    eobs_filenames.sort()

    clist = iris.cube.CubeList()
    for f in eobs_filenames:
        try:
            eobs_daily = iris.load_cube(f, all_con)
# Remove history in global attributes, as is stopping cube concatenation.
            eobs_daily.attributes = {}
# EOBS rainfall have units of mm day-1. Change the unit description to be CF-compliant.
            if var_name == 'pr':
                eobs_daily.standard_name = 'precipitation_amount'
                eobs_daily.units = 'kg m-2 day-1'
            clist.append(eobs_daily)
        except:
            pass

    return clist.concatenate_cube()


def process_iberia01(var_name, year_range, lon_lim, lat_lim, version, region_name, season):
    '''
    Reads in Iberia01 gridded rainfall data.
    Extracts the data for the given region and time period.
    Writes out the series and averaged data for the given region.

    var_name -- Name of variable, e.g., 'pr'
    year_range -- 2-element list containing the first and last years to be processed.
    lon_lim, lat_lim -- 2-element lists containing edges of region required
    version -- The version of the Iberia01 data, e.g., '1.0'
    region_name -- Name of the region, 'douro' or 'iberia'
    season -- The season name, e.g., 'amj', 'annual'
    '''

    indir = '/project/earthobs/IBERIA01/'
    filename = f'Iberia01_v{version}_DD_010reg_aa3d_{var_name}.nc'

# Set up constraints for the Iberian Peninsula, expanded as data will be regridded to a coarser resolution.
    delta = 2.0
    lon_con = iris.Constraint(longitude = lambda l: lon_lim[0]-delta <= l <= lon_lim[1]+delta)
    lat_con = iris.Constraint(latitude = lambda l: lat_lim[0]-delta <= l <= lat_lim[1]+delta)

    time_con = iris.Constraint(time=lambda cell: year_range[0] <= cell.point.year <= year_range[1])
    all_con = time_con & lon_con & lat_con

    ib_daily = iris.load_cube(os.path.join(indir, filename), all_con)
    ib_daily.standard_name = 'precipitation_amount'
    ib_daily.units = 'kg m-2 day-1'

    if season == 'annual':
# Calculate annual total rainfall
        iris.coord_categorisation.add_year(ib_daily, 'time', name='year')
        ib_series = ib_daily.aggregated_by('year', iris.analysis.SUM)
    else:
# Calculate seasonal total rainfall amounts
        all_months = 'jfmamjjasond'
        i = all_months.index(season)
        nmths = len(season)
        vine_seasons = [all_months[:i], all_months[i:i+nmths], all_months[i+nmths:]]

# Add the seasons and year as coordinates
# if seasons straddle the year boundaries, need to use 'season_year' instead
        iris.coord_categorisation.add_season(ib_daily, 'time', name='season', seasons=vine_seasons)
        iris.coord_categorisation.add_year(ib_daily, 'time', name='year')
        ib_series = ib_daily.aggregated_by(['season', 'year'], iris.analysis.SUM).extract(iris.Constraint(season = season))

# Add bounds to the coordinates of the Iberia01 data, if needed.
    if not ib_series.coord('longitude').has_bounds():
        ib_series.coord('longitude').guess_bounds()
    if not ib_series.coord('latitude').has_bounds():
        ib_series.coord('latitude').guess_bounds()

# Save the annual or seasonal series
    filename = f'iberia01_v{version}_{var_name}_{region_name}_{season}_series.nc'
    iris.save(ib_series, os.path.join(UDIR, filename))

# Average of annual or seasonal totals
    ib_series_mean = ib_series.collapsed('time', iris.analysis.MEAN)

# Save the averaged data
    filename = f'iberia01_v{version}_{var_name}_{region_name}_{season}_mean.nc'
    iris.save(ib_series_mean, os.path.join(UDIR, filename))


def process_depresys(var_name, year_range, lon_lim, lat_lim, version, region_name, season):
    '''
    Reads in Iberia01 gridded rainfall data.
    Extracts the data for the given region and time period.
    Writes out the series and averaged data for the given region.

    var_name -- Name of variable, e.g., 'pr'
    year_range -- 2-element list containing the first and last years to be processed.
    lon_lim, lat_lim -- 2-element lists containing edges of region required
    version -- The version of the DePreSys data, e.g., '3'
    region_name -- Name of the region, 'douro' or 'iberia'
    season -- The season name, e.g., 'amj', 'annual'
    '''

    dp3_path = '/project/decadal/haddn/DePreSys3/finalnew/netcdf/'

    dp3_months, ndays = get_dp3_filename_and_ndays(season)
    if season == 'annual':
        depresys3_filename = os.path.join(dp3_path, f'DP3precip_gpcc_st{dp3_months}satellite1ENS.nc')
    else:
        depresys3_filename = os.path.join(dp3_path, f'DP3precip_gpcc_st{dp3_months}satellite0ENS.nc')

    dp3_series = iris.load_cube(depresys3_filename)

# Add bounds to coordinates if not already present
    if not dp3_series.coord('longitude').has_bounds():
        dp3_series.coord('longitude').guess_bounds()
    if not dp3_series.coord('latitude').has_bounds():
        dp3_series.coord('latitude').guess_bounds()

# Change the cube's standard name and units; convert from mm day-1 to mm per season or year.
    dp3_series.standard_name = 'precipitation_amount'
    dp3_series.units = 'kg m-2 day-1'
    dp3_series.data *= ndays

# Calculate rainfall totals averaged over all years and realizations
    dp3_time_mean = dp3_series.collapsed('time', iris.analysis.MEAN)
    dp3_ens_mean = dp3_time_mean.collapsed('realization', iris.analysis.MEAN)

    ll_lim = (lon_lim[0], lon_lim[1], False, False)
    la_lim = (lat_lim[0], lat_lim[1], False, False)

    cube = dp3_ens_mean.intersection(longitude = ll_lim, latitude = la_lim)

# Save the processed data
    filename = f'DePreSys{version}_{var_name}_{region_name}_{season}_ensmean.nc'
    iris.save(cube, os.path.join(UDIR, filename))

    return cube


def get_dp3_filename_and_ndays(season):

    d = {'fma': ['4en6', 89], 'mam': ['5en7', 92], 'amj': ['6en8', 91], 'mjj': ['7en9', 92],
         'aso': ['10en12', 92], 'annual': ['3en14', 365.25]}

    if season in d:
        return d[season]
    else:
        raise ValueError('season {} not recognised'.format(season))

