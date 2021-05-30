#!/usr/bin/env python

import argparse

import cogamo.cogamo as cogamo

__author__ = 'Teruaki Enoto'
__version__ = '0.01'
# v0.01 : 2021-05-30 : original version

def get_parser():
	"""
	Creates a new argument parser.
	"""
	parser = argparse.ArgumentParser('cgm_convert_hkfile_to_fitsfile.py',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		description="""
Convert a raw csv-format CoGaMo house keeping remote data file to a fits-format event file.
		"""
		)
	version = '%(prog)s ' + __version__
	parser.add_argument('--version', '-v', action='version', version=version,
		help='show version of this command.')
	parser.add_argument('input_csv', type=str, 
		help='input raw csv-format house keeping remote data file obtained with the CoGaMo.')
	parser.add_argument('--output_fitsfile', '-o', type=str, default=None, 
		help='output fits-format event file. If the blank, the output file basename is the same as its input.')	
	#parser.add_argument('--config_file', '-c', type=str, default=None, 
	#	help='configure file.')		
	return parser

def main(args=None):
	parser = get_parser()
	args = parser.parse_args(args)

	file = cogamo.fopen(args.input_csv)
	file.write_to_fitsfile(output_fitsfile=args.output_fitsfile)

if __name__=="__main__":
	main()