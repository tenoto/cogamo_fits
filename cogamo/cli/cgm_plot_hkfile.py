#!/usr/bin/env python

import argparse

import cogamo.cogamo as cogamo

import matplotlib.pylab as plt 

__author__ = 'Teruaki Enoto'
__version__ = '0.01'
# v0.01 : 2020-08-14 : original version

def get_parser():
	"""
	Creates a new argument parser.
	"""
	parser = argparse.ArgumentParser('cgm_convert_hkfile_to_fitsfile.py',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		description="""
Convert a raw csv-format CoGaMo house keeping data file to a fits-format event file.
		"""
		)
	version = '%(prog)s ' + __version__
	parser.add_argument('--version', '-v', action='version', version=version,
		help='show version of this command.')
	parser.add_argument('input_hkfits', type=str, 
		help='input fits-format hk file.')
	return parser

def main(args=None):
	parser = get_parser()
	args = parser.parse_args(args)

	file = cogamo.fopen(args.input_hkfits)
	file.plot()

if __name__=="__main__":
	main()