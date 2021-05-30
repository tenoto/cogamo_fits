#!/usr/bin/env python

import os 
import sys
import datetime
import argparse
import subprocess

__author__ = 'Teruaki Enoto'
__version__ = '0.01'
# v0.01 : 2021-05-30 : original version

dict_cogamoid_to_servernum = {
	'37':'22', '38':'23'}

def get_parser():
	"""
	Creates a new argument parser.
	"""
	parser = argparse.ArgumentParser('cgm_wget_remotehk.py',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		description="""
This script downloads a remote csv-format CoGaMo house keeping data from a server. The Cogamo ID must be specified. When the -d (--date) option is specified, all data for that date will be downloaded. When the -s (--start) and -e (--end) options are specified as the start and end time, data within that time period will be downloaded. If no option is specified, the data for the last day will be downloaded.
		"""
		)
	version = '%(prog)s ' + __version__
	parser.add_argument('cgm_id', type=str, 
		help='Cogamo ID (e.g., 37)')	
	parser.add_argument('--version', '-v', action='version', version=version,
		help='show version of this command.')
	parser.add_argument('--start', '-s', type=str, default=None, 
		help='start time (e.g. 2021-05-25T00:00:00)')
	parser.add_argument('--end', '-e', type=str, default=None, 
		help='end time (e.g. 2021-05-26T00:00:00)')	
	parser.add_argument('--date', '-d', type=str, default=None, 
		help='download date (e.g. 2021-05-27')
		
	return parser

def wget_cgm_remotehk(cgm_id,start,end):
	print("%s" % sys._getframe().f_code.co_name)

	# Set output filename 
	passcode = os.getenv('COGAMO_SERVER_PASSCODE')
	output_csvfname = 'cgm%03d_rhk_' % int(cgm_id)
	output_csvfname += '%s_' % start.replace('-','').replace(':','')[2:15]
	output_csvfname += '%s' % end.replace('-','').replace(':','')[2:15]
	output_csvfname += '.csv'

	if os.path.exists(output_csvfname):
		cmd = 'rm -f %s'
		print(cmd);os.system(cmd)

	# Main routine for wget 
	cmd = 'wget "http://demo1.tacinc.jp/api/sensor/csv/'
	cmd += '?id=%s&' % dict_cogamoid_to_servernum[cgm_id]
	cmd += 'start_datetime=%s&' % start.replace('T',' ')
	cmd += 'end_datetime=%s&' % end.replace('T',' ')
	cmd += 'k=%s" ' % passcode
	cmd += '-O "%s"' % output_csvfname
	print(cmd);os.system(cmd)

	if not os.path.exists(output_csvfname):
		print("wget error...")
		exit()

	# Check file size.
	filesize_bytes = os.path.getsize(output_csvfname)
	if filesize_bytes/1e+3 <= 1.0:
		filesize_str = '%.1f bytes' % filesize_bytes
	elif filesize_bytes/1e+6 > 1.0:
		filesize_str = '%.1f MB' % (filesize_bytes/1e+6)
	else:
		filesize_str = '%.1f kB' % (filesize_bytes/1e+3)

	line_count = int(subprocess.check_output(['wc', output_csvfname]).decode().split('   ')[1])

	# output the result
	print("================================")
	print("Cogamo ID: %s" % cgm_id)
	print("Cogamo server ID: %s" % dict_cogamoid_to_servernum[cgm_id])	
	print("start: %s" % start)
	print("end  : %s" % end)	
	print("output_csvfname: %s" % output_csvfname)
	print("file size: %s" % filesize_str)
	print("line count: %d" % line_count)
	print("================================")

def main(args=None):
	parser = get_parser()
	args = parser.parse_args(args)

	if args.date != None:
		start = '%sT00:00:00' % args.date 
		end = '%sT23:59:59' % args.date
		wget_cgm_remotehk(args.cgm_id,start,end)
	elif args.start != None and args.end != None:
		wget_cgm_remotehk(args.cgm_id,args.start,args.end)
	else:
		dt_now = datetime.datetime.now() 
		end = dt_now.strftime('%Y-%m-%dT%H:%M:%S')
		dt_start = dt_now - datetime.timedelta(hours=24)		
		start = dt_start.strftime('%Y-%m-%dT%H:%M:%S')
		wget_cgm_remotehk(args.cgm_id,start,end)

if __name__=="__main__":
	main()
