import os
import iris


def make_filename(path, dataset_name, version, season):

    if dataset_name == 'DePreSys':
        fend = 'ensmean'
    else:
        fend = 'mean'

    filename = f'{dataset_name}_v{version}_pr_iberia_{season}_{fend}.nc'

    return os.path.join(path, filename)


def regrid_datasets(datadir, datasets, season_names, region):

    dout = '/data/users/hadmi/MED-GOLD/UNSEEN/agg_to_dp3'

# Load in the DePreSys data
    dataset_name = 'DePreSys'
    version = datasets[dataset_name]
    filename = make_filename(datadir, dataset_name, version, season)
    dp3_cube = iris.load_cube(filename)

    for dataset_name in datasets:
        version = datasets[dataset_name]
        for season in season_names:
            filename = make_filename(datadir, dataset_name, version, season)
            data_cube = iris.load_cube(filename)

# Assign a coordinate system to the CHIRPS data (set to None in the files). Regridding
# fails if coordinate system not specified.
            data_cube.coord('longitude').coord_system = dp3_cube.coord('longitude').coord_system
            data_cube.coord('latitude').coord_system = dp3_cube.coord('latitude').coord_system

# Regrid the averaged rainfall totals to the coarser DePreSys grid.
            data_dp3 = data_cube.regrid(dp3_cube, iris.analysis.AreaWeighted())

            ofilename = make_filename(dout, dataset_name, version, season)
            iris.save(data_dp3, ofilename)


def main():

    datadir = '/data/users/hadmi/MED-GOLD/UNSEEN/native_grids/'

    region = 'iberia'
    season_names = ['annual', 'amj', 'aso']
    datasets = {'chirps': '2.0', 'iberia01': '1.0', 'eobs': '21'}

    regrid_datasets(datadir, datasets, season_names, region)


if __name__ == '__main__':
    main()
