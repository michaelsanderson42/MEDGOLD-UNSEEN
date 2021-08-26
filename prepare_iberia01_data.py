import os
import glob
import iris


if __name__ == '__main__':
    '''
    Need to regrid Iberia01 data (0.1 degree resolution) to DePreSys3 (60 km).
    Iris cube regrid with area weighting, set all data points with some missing data
    to missing data. Not sure why, as worked properly for other datasets.

    Have to use cdo after setting missing data points to zero - see
    Tip just before half-way down on the web page below:
    https://code.mpimet.mpg.de/projects/cdo/wiki/Tutorial#Interpolation

    This program reads in the Iberia01 data, removes the mask, sets all missing
    data points to zero, and saves the modified data to a temporay area
    '''

    datadir = '/data/users/hadmi/MED-GOLD/UNSEEN/'
    indir = 'native_grids'
    tmpdir = 'tmp'

    filenames = glob.glob(os.path.join(datadir, indir, 'iberia01_v1.0_pr_iberia*nc'))
    filenames.sort()

    for filename in filenames:
        print('Processing '+os.path.basename(filename))
        cube = iris.load_cube(filename)
        cube.data.data[cube.data.mask] = 0.0
        cube.data.mask = False

        fout = os.path.join(datadir, tmpdir, os.path.basename(filename))
        iris.save(cube, fout)
