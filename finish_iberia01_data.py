import os
import glob
import iris


if __name__ == '__main__':
    '''
    Need to add a mask back onto the regridded Iberia01 data.
    Iris cube regrid with area weighting, set all data points with some missing data
    to missing data. Not sure why, as worked properly for other datasets.

    Regridding done using cdo,remapcon
    '''

    datadir = '/data/users/hadmi/MED-GOLD/UNSEEN/'
    indir = 'native_grids'
    tmpdir = 'tmp'
    outdir = 'agg_to_dp3'

# Read in the aggregated CHIRPS data, to get the missing data value (rmdi)
    chirps = iris.load_cube(os.path.join(datadir, indir, 'chirps_v2.0_pr_iberia_annual_mean.nc'))
    rmdi = chirps.data._fill_value
    print('Fill value is ', rmdi)

# Get the filenames of the Iberia01 data on the DePreSys3 grid, without a mask.
    filenames = glob.glob(os.path.join(datadir, tmpdir, 'iberia01_v1.0_pr_iberia*dp3_nomask.nc'))
    filenames.sort()

    for filename in filenames:
        ftmp = os.path.basename(filename)
        print('Processing '+ftmp)
        cube = iris.load_cube(filename)
        mask = (cube.data.data == 0.0)
        cube.data.data[mask] = rmdi
        cube.data.mask = mask

        i = ftmp.index('dp3')
        fout = ftmp[:i-1] + '.nc'
#       print(fout)
#       print(os.path.join(datadir, outdir, fout))
        iris.save(cube, os.path.join(datadir, outdir, fout))

