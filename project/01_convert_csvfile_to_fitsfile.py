#!/usr/bin/env python

import os
import glob 

INDIR = '/Users/enoto/Dropbox/01_enoto/research/growth/data/20200804_CoGaMo_data_sharing'
#OUTDIR = 'out/20200804_CoGaMo_data_sharing'
OUTDIR = '/Users/enoto/Dropbox/01_enoto/research/growth/data/20200804_CoGaMo_data_sharing/out'

cmd = 'mkdir -p %s' % OUTDIR
print(cmd);os.system(cmd)


for det_id in ['011']:
	outdir_sub = '%s/%s' % (OUTDIR,det_id)
	cmd = 'mkdir -p %s/{hk,evt};' % outdir_sub
	print(cmd);os.system(cmd)

	file_config = '%s/%s/config.csv' % (INDIR,det_id)

	for csvfile_path in glob.glob('%s/%s/log/*csv' % (INDIR,det_id)):
		print(csvfile_path)
		cmd  = 'cogamo/cli/cgm_convert_hkfile_to_fitsfile.py '
		cmd += '%s ' % (csvfile_path)
		cmd += '-c %s' % file_config
		print(cmd);os.system(cmd)

		basename = os.path.splitext(os.path.basename(csvfile_path))[0]
		hkfits = '%s_hk.fits' % basename
		cmd = 'mv %s %s/hk' % (hkfits,outdir_sub)
		print(cmd);os.system(cmd)

	for csvfile_path in glob.glob('%s/%s/data/*csv' % (INDIR,det_id)):
		print(csvfile_path)
		cmd  = 'cogamo/cli/cgm_convert_rawcsv_evtfile_to_fitsfile.py '
		cmd += '%s ' % (csvfile_path)
		cmd += '-c %s' % file_config
		print(cmd);os.system(cmd)

		basename = os.path.splitext(os.path.basename(csvfile_path))[0]
		hkfits = '%s.evt' % basename
		cmd = 'mv %s %s/evt' % (hkfits,outdir_sub)
		print(cmd);os.system(cmd)

