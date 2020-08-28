#!/usr/bin/env python

import os
import glob 

OUTDIR = '/Users/enoto/Dropbox/01_enoto/research/growth/data/20200804_CoGaMo_data_sharing/out' 

#for det_id in ['011','019']:
#for det_id in ['019']:
for det_id in ['011']:
	file_config = '%s/%s/config.csv' % (OUTDIR,det_id)

	datestr = '20200305'
	outdir_sub = '%s/%s/plot/evt/%s' % (OUTDIR,det_id,datestr)
	cmd = 'mkdir -p %s;' % outdir_sub
	print(cmd);os.system(cmd)

	for evtfile_path in glob.glob('%s/%s/evt/*.evt' % (OUTDIR,det_id)):
		print(evtfile_path)

		cmd  = 'cogamo/cli/cgm_plot_curve.py '
		cmd += '%s ' % evtfile_path
		cmd += '--pha_min 300 --tbin 1 '
		print(cmd);os.system(cmd)

		"""
		basename = os.path.splitext(os.path.basename(evtfile_path))[0]
		hkfits = '%s_hk.fits' % basename
		cmd = 'mv %s %s/hk' % (hkfits,outdir_sub)
		print(cmd);os.system(cmd)
		"""
