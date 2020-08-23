#!/usr/bin/env python

import argparse

import cogamo.cogamo as cogamo

__author__ = 'Teruaki Enoto'
__version__ = '0.01'
# v0.01 : 2020-08-14 : original version

def get_parser():
	"""
	Creates a new argument parser.
	"""
	parser = argparse.ArgumentParser('cgm_plot_pha.py',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		description="""
plot pha spectrum from an event fitsfile.
		"""
		)
	version = '%(prog)s ' + __version__
	parser.add_argument('--version', '-v', action='version', version=version,
		help='show version of this command.')
	parser.add_argument('input_evtfits', type=str, 
		help='input fits-format event file.')
	parser.add_argument('--pha_min', type=int, default=None,
		help='pha_min')	
	parser.add_argument('--pha_max', type=int, default=None,
		help='pha_max')		
	return parser

def main(args=None):
	parser = get_parser()
	args = parser.parse_args(args)

	file = cogamo.fopen(args.input_evtfits)
	file.plot_curve(pha_min=args.pha_min,pha_max=args.pha_max)

if __name__=="__main__":
	main()