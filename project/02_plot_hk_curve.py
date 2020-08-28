#!/usr/bin/env python

import os
import glob 

OUTDIR = '/Users/enoto/Dropbox/01_enoto/research/growth/data/20200804_CoGaMo_data_sharing/out' 

#for det_id in ['011','019']:
#for det_id in ['011']:
for det_id in ['019']:
	outdir_sub = '%s/%s/plot/hk' % (OUTDIR,det_id)
	cmd = 'mkdir -p %s;' % outdir_sub
	print(cmd);os.system(cmd)

	file_config = '%s/%s/config.csv' % (OUTDIR,det_id)

	for hkfile_path in glob.glob('%s/%s/hk/*.fits' % (OUTDIR,det_id)):
		print(hkfile_path)

		cmd = 'cogamo/cli/cgm_plot_hkfile.py %s ' % hkfile_path
		print(cmd);os.system(cmd)

		basename = os.path.splitext(os.path.basename(hkfile_path))[0]
		hkpdf = '%s.pdf' % basename
		cmd = 'mv %s %s' % (hkpdf,outdir_sub)
		print(cmd);os.system(cmd)


	#for evtfile_path in glob.glob('%s/%s/evt/*.evt' % (OUTDIR,det_id)):
	#	print(evtfile_path)

	"""		
		cmd  = 'cogamo/cli/cgm_convert_hkfile_to_fitsfile.py '
		cmd += '%s ' % (csvfile_path)
		cmd += '-c %s' % file_config
		print(cmd);os.system(cmd)

		basename = os.path.splitext(os.path.basename(csvfile_path))[0]
		hkfits = '%s_hk.fits' % basename
		cmd = 'mv %s %s/hk' % (hkfits,outdir_sub)
		print(cmd);os.system(cmd)
	"""		
	"""
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
	"""		

