#!/usr/bin/env python

import argparse

import cogamo.cogamo as cogamo

__author__ = 'Teruaki Enoto'
__version__ = '0.01'
# v0.01 : 2020-09-27 : original version

def get_parser():
	"""
	Creates a new argument parser.
	"""
	parser = argparse.ArgumentParser('cgm_fit_phaline.py.py',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		description="""
fit a line of a spectrum (pha) file.
		"""
		)
	version = '%(prog)s ' + __version__
	parser.add_argument('--version', '-v', action='version', version=version,
		help='show version of this command.')
	parser.add_argument('input_evtfits', type=str, 
		help='input fits-format event file.')
	parser.add_argument('--xmin', type=float, help='xmin.')	
	parser.add_argument('--xmax', type=float, help='xmax.')		
	return parser

def main(args=None):
	parser = get_parser()
	args = parser.parse_args(args)

	#file = cogamo.fopen(args.input_evtfits)
	#file.plot_pha_example()
	srcevt = cogamo.EventFitsFile(args.input_evtfits)
	srcevt.plot_curve(tbin=30,pha_min=30)
	srcevt.plot_pha_example()
	srcevt.fit_line(xmin=args.xmin,xmax=args.xmax)	

if __name__=="__main__":
	main()