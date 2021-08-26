'''
    Creates plots showing gridded precipitation data from DePreSys and three other
    observational datasets
'''
    
import os
import iris
import iris.plot as iplt
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy


def make_filename(path, dataset_name, version, season):
    '''
    Construct the filename for the given dataset

    path -- Directory where the data are stored
    dataset_name -- Name of the dataset
    version -- Dataset version
    season -- Name of the season; could also be 'annual'

    Returns: the filename, inclusing the full path
    '''

    if dataset_name == 'DePreSys':
        fend = 'ensmean'
        filename = f'{dataset_name}{version}_pr_iberia_{season}_{fend}.nc'
    else:
        fend = 'mean'
        filename = f'{dataset_name}_v{version}_pr_iberia_{season}_{fend}.nc'

    return os.path.join(path, filename)


def plot_depresys_obs(datadir, datasets, season_names, region):
    '''
    Creates a figure consisting of four panels, showing average gridded precipitation
    from DePreSys and observational datasets

    datadir -- Directory where the gridded data are stored
    datasets -- Dict containing names of the datasets and their versions
    season_names -- Names of the seasons - amj, annual
    region -- Name of the region under study
    '''

    plot_titles = {'DePreSys': 'DePreSys', 'eobs': 'E-OBS', 'chirps': 'CHIRPS',
        'iberia01': 'Iberia01'}

    for season in season_names:
        print(season)

# Set up the levels and colours for plotting
        if season == 'annual':
            levels = [200.0, 300.0, 400.0, 500.0, 600.0, 700.0, 800.0, 1000.0, 1400.0, 1800.0, 2200.0]
            cb_ticks = [200.0, 400.0, 600.0, 800.0, 1000.0, 1400.0, 1800.0, 2200.0]
        else:
            levels = [50.0*i for i in list(range(1, 12))]
            cb_ticks = [100, 200, 300, 400, 500]

        cmap = plt.get_cmap("YlGnBu")
        norm = mcolors.BoundaryNorm(boundaries=levels, ncolors=256)

        fig = plt.figure(figsize=(11.7,8.3))

        for j, dataset_name in enumerate(datasets):
            print(j, dataset_name)
            version = datasets[dataset_name]
            filename = make_filename(datadir, dataset_name, version, season)
            data_cube = iris.load_cube(filename)

            plt.subplot(2, 2, j+1)
            block_result = iplt.pcolormesh(data_cube, cmap=cmap, norm=norm)
            plt.title(plot_titles[dataset_name])
            plt.gca().coastlines()
            plt.gca().add_feature(cartopy.feature.BORDERS)

# Get the positions of the 2nd plot and the left position of the 1st plot
            if j == 2:
                left1, bottom1, width1, height1 = plt.gca().get_position().bounds
            if j == 3:
                left2, bottom2, width2, height2 = plt.gca().get_position().bounds 

# Add axes to the figure, to place the colour bar
        cb_left = left1
        cb_height = 0.03
        cb_bottom = bottom2 - 0.05
        gap_between_plots = left2 - (left1 + width1)
        cb_width = width1 + width2 + gap_between_plots
        colorbar_axes = fig.add_axes([cb_left, cb_bottom, cb_width, cb_height])

# Add the colour bar
        cbar = plt.colorbar(block_result, colorbar_axes, orientation='horizontal', ticks=cb_ticks)
        cbar.set_label("Seasonal Rainfall / mm")

        fdir = '/home/h03/hadmi/Python/MedGOLD/UNSEEN/figures/'
        if season == 'amj':
            fhead = 'Fig3_'
        elif season == 'aso':
            fhead = 'Fig4_'
        else:
            fhead = 'FigS1_'
        filename = fhead + f'DePreSys_obs_{season}.png'
        plt.savefig(os.path.join(fdir, filename), dpi=300)
        plt.close()
#       plt.show()


def main():

    datadir = '/data/users/hadmi/MED-GOLD/UNSEEN/agg_to_dp3/'
    region = 'iberia'
    season_names = ['annual', 'amj', 'aso']
    datasets = {'DePreSys': '3', 'chirps': '2.0', 'iberia01': '1.0', 'eobs': '21'}

    plot_depresys_obs(datadir, datasets, season_names, region)


if __name__ == '__main__':
    main()
