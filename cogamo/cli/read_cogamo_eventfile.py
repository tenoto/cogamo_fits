#!/usr/bin/env python

import argparse

import cogamo.cogamo as cogamo

__author__ = 'Teruaki Enoto'
__version__ = '0.01'
# v0.01 : 2020-08-08 : original version

def get_parser():
	"""
	Creates a new argument parser.
	"""
	parser = argparse.ArgumentParser('read_cogamo_eventfile.py',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		description="""
description 
		"""
		)
	version = '%(prog)s ' + __version__
	parser.add_argument('--version', '-v', action='version', version=version,
		help='show version of this command.')
	parser.add_argument('event_file', type=str, 
		help='event file')
	return parser

def main(args=None):
	parser = get_parser()
	args = parser.parse_args(args)

	file = cogamo.open(args.event_file)
	file.show_data_summary()
	file.set_filename_property()
	file.write_to_fitsfile()

if __name__=="__main__":
	main()