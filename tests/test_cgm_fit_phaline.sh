#!/bin/sh -f

export DATADIR="/Users/enoto/work/dropbox/01_enoto/research/growth/logbook/200926_CoGaMo_137Cs/"

cogamo/cli/cgm_fit_phaline.py $DATADIR/030_20200917_30_Cs137_ut1600317300to1600320600.evt \
	--xmin 35 --xmax 65