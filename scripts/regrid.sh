datadir=/data/users/hadmi/MED-GOLD/UNSEEN
tmpdir=${datadir}/tmp

target_grid=${datadir}/native_grids/DePreSys3_pr_iberia_annual_ensmean.nc

filenames=`ls ${tmpdir}`

for f in $filenames
do
    echo $f
    fin=${tmpdir}/$f
    ftmp=`echo $f | rev | cut -f 2- -d '.' | rev`
    fout=${tmpdir}/${ftmp}_dp3_nomask.nc
    cdo remapcon,$target_grid $fin $fout
done
