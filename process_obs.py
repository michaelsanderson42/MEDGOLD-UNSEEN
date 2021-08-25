from lib.process import process_chirps, process_eobs, process_iberia01, process_depresys

def main():
    '''
    Processes gridded observations, to create series of annual and seasonal total rainfall,
    and averages.
    '''

# The Iberian Peninsula. Coordinates obtained from the Iberia01 dataset
# in /project/earthobs/IBERIA01
    region_name = 'iberia'
    lon_lim = (-9.5,  4.3)
    lat_lim = (36.0, 43.8)

    var_name = 'pr'
    year_range = [1980, 2017]  #  Matches DePreSys hindcast period

# Version numbers of datasets
    eobs_version = '21'
    depresys_version = '3'
    iberia01_version = '1.0'
    chirps_version = '2.0'

# Create annual and seasonal totals, for the two vine seasons (growth and maturation/harvest)
# Specify the seasons as sequences of months - amj is April, May, June
    for season in ['annual', 'amj', 'aso']:
        print(season)
        process_chirps(var_name, year_range, lon_lim, lat_lim, chirps_version, region_name, season)
        process_eobs(var_name, year_range, lon_lim, lat_lim, eobs_version, region_name, season)
        process_iberia01(var_name, year_range, lon_lim, lat_lim, iberia01_version, region_name, season)
        process_depresys(var_name, year_range, lon_lim, lat_lim, depresys_version, region_name, season)


if __name__ == '__main__':
    main()
