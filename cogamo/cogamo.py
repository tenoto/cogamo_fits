# -*- coding: utf-8 -*-

import os
import re
import sys
import numpy as np
import pandas as pd

import astropy.units as u
from astropy.io import fits
from astropy.time import Time
from astropy.time import TimeDelta 

TimeDelta_JST2UTC = TimeDelta(9.0*60*60, format='sec')

class EventFile(object):
	def __init__(self):
		self.nevents = 0
		self.file_path = None

	def show_data_summary(self):
		sys.stdout.write(str(self))

	def __str__(self):
		dump  = 'Format: {}'.format(self.format)		
		dump += 'Nevents: {}'.format(self.nevents)
		dump += '\n'
		return dump

class EventFitsFile(EventFile):
	"""Represents EventFile in the FITS format.
	:param file_path: path to a file to be opened
	"""
	def __init__(self, file_path):
		self.file_path = file_path

		self.basename = os.path.splitext(os.path.basename(self.file_path))[0]

		if not os.path.exists(self.file_path):
			raise FileNotFoundError("{} not found".format(self.file_path))
		try:
			self.hdu = fits.open(self.file_path)
		except OSError as e:
			raise

		self.format = 'fits'
		self.nevents = len(self.hdu['EVENTS'].data)				

class CogamoRawcsvEventFile(EventFile):
	"""Represents EventFile in the CSV format for a CoGamo detector.
	:param file_path: path to a file to be opened
	"""
	def __init__(self, file_path):
		self.file_path = file_path

		self.basename = os.path.splitext(os.path.basename(self.file_path))[0]

		if not os.path.exists(self.file_path):
			raise FileNotFoundError("{} not found".format(self.file_path))
		try:
			self.df = pd.read_csv(self.file_path, index_col=False, 
				names=['minute','sec','decisec','pha'],
				dtype={'minute':np.uintc,'sec':np.uintc,'decisec':np.uint16,'pha':np.uint16})
			self.detid, self.yyyymmdd, self.hh = self.basename.split('_')
		except OSError as e:
			raise

		self.format = 'rawcsv'
		self.nevents = len(self.df)

		self.set_filename_property()

	def set_filename_property(self):
		self.detid_str, self.yyyymmdd_jst, self.hour_jst = os.path.splitext(os.path.basename(self.file_path))[0].split("_")		

	def set_config_file(self,config_file):
		self.config = CogamoConfigFile(config_file)

	def set_time_series(self):
		year = self.yyyymmdd_jst[0:4]
		month = self.yyyymmdd_jst[4:6]
		day = self.yyyymmdd_jst[6:8]		
		str_time = '%04d-%02d-%02dT%02d:' % (int(year),int(month),int(day),int(self.hour_jst))
		self.time_series_str  = np.char.array(np.full(self.nevents, str_time)) + np.char.mod('%02d:',self.df['minute']) + np.char.mod('%02d.',self.df['sec']) + + np.char.mod('%04d',self.df['decisec'])
		self.time_series_jst = Time(self.time_series_str, format='isot', scale='utc') 
		self.time_series_utc = self.time_series_jst - TimeDelta_JST2UTC
		print(self.time_series_jst)
		print(self.time_series_utc)
		print(self.time_series_jst.unix[0])
		print(self.time_series_utc.unix[0])		
		exit()

	def write_to_fitsfile(self,output_fitsfile=None,config_file=None):
		"""
		https://docs.astropy.org/en/stable/io/fits/usage/table.html
		"""
		sys.stdout.write('----- {} -----\n'.format(sys._getframe().f_code.co_name))

		if output_fitsfile == None:
			output_fitsfile = "{}.evt".format(self.basename)
		elif os.path.exists(output_fitsfile):
			raise FileExistsError("{} has alaredy existed.".format(output_fitsfile))

		self.set_time_series()

		column_minute = fits.Column(name='minute',format='B', unit='minute', array=self.df['minute'])
		column_sec = fits.Column(name='sec',format='B', unit='sec', array=self.df['sec'])
		column_decisec = fits.Column(name='decisec',format='I', unit='100 microsec', array=self.df['decisec'])						
		column_pha = fits.Column(name='pha',format='I', unit='channel', array=self.df['pha'])

		column_defs = fits.ColDefs([column_minute,column_sec,column_decisec,column_pha])
		hdu = fits.BinTableHDU.from_columns(column_defs,name='EVENTS')

		dict_keywords = {
			'DET_ID':[self.detid_str,'Detector_ID'],
			'YYYYMMDD':[self.yyyymmdd_jst,'Year, month, and day in JST of the file'],			
			'Hour':[self.hour_jst,'Hour in JST of the file']
			}
		for keyword in dict_keywords.keys():
			hdu.header[keyword] = dict_keywords[keyword][0]
			hdu.header.comments[keyword] = dict_keywords[keyword][1]

		if config_file != None:
			self.set_config_file(config_file)
			for keyword in self.config.dict_keywords.keys():
				hdu.header[keyword] = self.config.dict_keywords[keyword]

		hdu.writeto(output_fitsfile)

class CogamoConfigFile():
	def __init__(self, file_path):
		self.file_path = file_path

		self.dict_keywords = {}
		if not os.path.exists(self.file_path):
			raise FileNotFoundError("{} not found".format(self.file_path))
		try:
			f = open(self.file_path)
			for line in f:
				keyword, value = line.split(',')
				self.dict_keywords[keyword] = int(value)
			f.close()
		except OSError as e:
			raise

	def get_dict_keywords(self):
		return self.dict_keywords

def cogamo_open(file_path):
	if ".fits" in file_path:
		return EventFitsFile(file_path)
	elif re.fullmatch(r'\d{3}_\d{8}_\d{2}.csv', os.path.basename(file_path)):
		return CogamoRawcsvEventFile(file_path)
	else:
		raise NotImplementedError("EventFile class for this file type is not implemented")		
