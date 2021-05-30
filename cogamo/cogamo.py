# -*- coding: utf-8 -*-

import os
import re
import sys
import numpy as np
import pandas as pd

import astropy.units as u
from astropy.io import fits
from astropy.time import Time

from datetime import timedelta, timezone
tz_tokyo = timezone(timedelta(hours=+9), 'Asia/Tokyo')
tz_utc = timezone(timedelta(hours=0), 'UTC')

import matplotlib.dates as dates
import matplotlib.pylab as plt 
from astropy.visualization import time_support
import matplotlib

from iminuit import Minuit
from probfit import BinnedChi2, UnbinnedLH, Extended, gaussian


##########################
# General functions
##########################

def gauss_continuum(x, mu, sigma, area, c0=0.0, c1=0.0):
    return area * np.exp(-0.5*(x-mu)**2/sigma**2)/(np.sqrt(2*np.pi)*sigma) + c0 + c1 * x 

class Hist1D(object):

	def __init__(self, nbins, xlow, xhigh):
		self.nbins = nbins
		self.xlow  = xlow
		self.xhigh = xhigh
		#print(self.nbins,self.xlow,self.xhigh)
		self.hist, edges = np.histogram([], bins=nbins, range=(xlow, xhigh))
		self.bins = (edges[:-1] + edges[1:]) / 2.
		#print(self.hist,edges,self.bins)

	def fill(self, arr):
		#print(arr)
		hist, edges = np.histogram(arr, bins=self.nbins, range=(self.xlow, self.xhigh))
		self.hist += hist

	@property
	def data(self):
		return self.bins, self.hist

##########################
# Event fits file
##########################

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

	def plot_pha_example(self):
		"""
		This is just an example code, not perfect as a library. 
		"""
		sys.stdout.write('----- {} -----\n'.format(sys._getframe().f_code.co_name))
	
		data = self.hdu['EVENTS'].data

		outpdf = '%s_pha.pdf' % self.basename

		y, xedges, patches = plt.hist(data['pha'],range=(0,2**10),bins=2**9,histtype='step')
		x = 0.5*(xedges[1:] + xedges[:-1])

		fig, ax = plt.subplots(1,1, figsize=(11.69,8.27))

		plt.errorbar(x,y,yerr=np.sqrt(y),marker='',drawstyle='steps-mid')

		fontsize = 18
		plt.xlabel('ADC channel (pha)', fontsize=fontsize)
		plt.ylabel('Counts', fontsize=fontsize)
		plt.xscale('log')				
		plt.yscale('log')
		plt.xlim(15,2**10)
		plt.tight_layout(pad=2)
		plt.tick_params(labelsize=fontsize)
		plt.rcParams["font.family"] = "serif"
		plt.rcParams["mathtext.fontset"] = "dejavuserif"		

		ax.minorticks_on()
		ax.grid(True)
		ax.grid(axis='both',which='major', linestyle='--', color='#000000')
		ax.grid(axis='both',which='minor', linestyle='--')	
		ax.tick_params(axis="both", which='major', direction='in', length=5)
		ax.tick_params(axis="both", which='minor', direction='in', length=3)	

		plt.savefig(outpdf)

	def plot_curve(self,tbin=1.0,pha_min=None,pha_max=None,colname="TIME"):
		sys.stdout.write('----- {} -----\n'.format(sys._getframe().f_code.co_name))


		data = self.hdu['EVENTS'].data

		if pha_min == None and pha_max == None:
			print("no pha selection.")
			suffix = 'pha_all' 
			mask = np.full(len(data), True)
		elif pha_min != None and pha_max == None:
			print("%d <= pha" % pha_min)	
			suffix = 'pha_%d_xx'	% (pha_min)								
			mask = (data['pha'] >= pha_min)
		elif pha_min == None and pha_max != None:
			print("pha <= %d" % pha_max)				
			suffix = 'pha_xx_%d' % (pha_max)													
			mask = (data['pha'] <= pha_max)
		elif pha_min != None and pha_max != None:
			print("%d <= pha <= %d" % (pha_min,pha_max))
			suffix = 'pha_%d_%d'	% (pha_min,pha_max)			
			mask = np.logical_and((data['pha'] >= pha_min),(data['pha'] <= pha_max))

		outpdf = '%s_curve_%s.pdf' % (self.basename,suffix)

		print("%d --> %d (%.2f%%)" % (len(data),len(data[mask]),
			float(len(data[mask]))/float(len(data))*100.0))

		xlow = 0.0
		xhigh = data['TIME'][-1] - data['TIME'][0]
		nbins = round((xhigh-xlow)/tbin)
		hist_lc = Hist1D(nbins, xlow, xhigh)
		print(data['TIME'][mask]-data['TIME'][0])
		hist_lc.fill(data['TIME'][mask]-data['TIME'][0])

		fig, ax = plt.subplots(1,1, figsize=(11.69,8.27))		
		plt.step(*hist_lc.data)

		"""
		plt.errorbar(x,y,yerr=np.sqrt(y),marker='',drawstyle='steps-mid')

		fontsize = 18
		plt.xlabel('ADC channel (pha)', fontsize=fontsize)
		plt.ylabel('Counts', fontsize=fontsize)
		plt.xscale('log')				
		plt.yscale('log')
		plt.xlim(15,2**10)
		plt.tight_layout(pad=2)
		plt.tick_params(labelsize=fontsize)
		plt.rcParams["font.family"] = "serif"
		plt.rcParams["mathtext.fontset"] = "dejavuserif"		

		ax.minorticks_on()
		ax.grid(True)
		ax.grid(axis='both',which='major', linestyle='--', color='#000000')
		ax.grid(axis='both',which='minor', linestyle='--')	
		ax.tick_params(axis="both", which='major', direction='in', length=5)
		ax.tick_params(axis="both", which='minor', direction='in', length=3)	
		"""

		plt.savefig(outpdf)	

	def fit_line(self,pdfname='fit.pdf',fitout='fit.txt',xmin=None,xmax=None,fontsize=18):
		sys.stdout.write('----- {} -----\n'.format(sys._getframe().f_code.co_name))

		flag = np.logical_and(self.hdu['EVENTS'].data['pha'] >= xmin, self.hdu['EVENTS'].data['pha'] <= xmax)
		selected_evt = self.hdu['EVENTS'].data['pha'][flag]
		nbins = int(xmax - xmin + 1)
		bc2 = BinnedChi2(gauss_continuum, selected_evt, 
			bins=nbins, bound=(xmin,xmax))

		fig, ax = plt.subplots(1,1, figsize=(11.69,8.27))
		plt.xlabel('ADC channel (pha)', fontsize=fontsize)
		plt.ylabel('Counts', fontsize=fontsize)		
		plt.tight_layout(pad=2)
		plt.tick_params(labelsize=fontsize)
		plt.rcParams["font.family"] = "serif"
		plt.rcParams["mathtext.fontset"] = "dejavuserif"	
		ax.minorticks_on()
		ax.grid(True)
		ax.grid(axis='both',which='major', linestyle='--', color='#000000')
		ax.grid(axis='both',which='minor', linestyle='--')	
		ax.tick_params(axis="both", which='major', direction='in', length=5)						

		m = Minuit(bc2, mu=52, sigma=5, area=100, c0=0, c1=0)
		m.migrad()
		bc2.draw(m,errors=True)
		m.minos() 
		m.print_param()
		print(m.values)
		print(m.errors)
		print(m.merrors)
		plt.savefig(pdfname)	

	def find_burst(self,pha_min=None,pha_max=None,
		tbin=1.0,threshold=3.0,colname="TIME"):
		sys.stdout.write('----- {} -----\n'.format(sys._getframe().f_code.co_name))

		data = self.hdu['EVENTS'].data

		if pha_min == None and pha_max == None:
			print("no pha selection.")
			suffix = 'pha_all' 
			mask = np.full(len(data), True)
		elif pha_min != None and pha_max == None:
			print("%d <= pha" % pha_min)	
			suffix = 'pha_%d_xx'	% (pha_min)								
			mask = (data['pha'] >= pha_min)
		elif pha_min == None and pha_max != None:
			print("pha <= %d" % pha_max)				
			suffix = 'pha_xx_%d' % (pha_max)													
			mask = (data['pha'] <= pha_max)
		elif pha_min != None and pha_max != None:
			print("%d <= pha <= %d" % (pha_min,pha_max))
			suffix = 'pha_%d_%d'	% (pha_min,pha_max)			
			mask = np.logical_and((data['pha'] >= pha_min),(data['pha'] <= pha_max))

		print("%d --> %d (%.2f%%)" % (len(data),len(data[mask]),
			float(len(data[mask]))/float(len(data))*100.0))

		xlow = 0.0
		xhigh = data['TIME'][-1] - data['TIME'][0]
		nbins = round((xhigh-xlow)/tbin)
		hist_lc = Hist1D(nbins, xlow, xhigh)
		#print(data['TIME'][mask]-data['TIME'][0])
		hist_lc.fill(data['TIME'][mask]-data['TIME'][0])

		outpdf = 'tmp_%s_curve_%s.pdf' % (self.basename,suffix)
		fig, ax = plt.subplots(1,1, figsize=(11.69,8.27))		
		plt.step(*hist_lc.data)		
		plt.savefig(outpdf)	

		xlow = 0
		xhigh = max(hist_lc.hist) * 1.2
		nbins = round(xhigh)
		hist_dist = Hist1D(nbins,xlow,xhigh)
		hist_dist.fill(hist_lc.hist)

		outpdf = 'tmp_%s_curve_%s_dist.pdf' % (self.basename,suffix)
		fig, ax = plt.subplots(1,1, figsize=(11.69,8.27))		
		plt.step(*hist_dist.data)		
		plt.yscale('log')
		plt.savefig(outpdf)	

class EventRawcsvFile(EventFile):
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
		self.config = ConfigFile(config_file)

	def set_time_series(self):
		"""
		the standard unix time does not have enough accuracy below 1 second.
		Sub-second time stamp is handled by another column
		"""
		year = self.yyyymmdd_jst[0:4]
		month = self.yyyymmdd_jst[4:6]
		day = self.yyyymmdd_jst[6:8]		
		str_time = '%04d-%02d-%02dT%02d:' % (int(year),int(month),int(day),int(self.hour_jst))
		self.time_series_str  = np.char.array(np.full(self.nevents, str_time)) + np.char.mod('%02d:',self.df['minute']) + np.char.mod('%02d',self.df['sec']) + np.char.mod('.%04d',self.df['decisec']) 
		time_series_jst = Time(self.time_series_str, format='isot', scale='utc', precision=5) 
		self.time_series_utc = time_series_jst - timedelta(hours=+9)

	def write_to_fitsfile(self,output_fitsfile=None,config_file=None,flag_TIME=True):
		"""
		https://docs.astropy.org/en/stable/io/fits/usage/table.html
		"""
		sys.stdout.write('----- {} -----\n'.format(sys._getframe().f_code.co_name))

		if output_fitsfile == None:
			output_fitsfile = "{}.evt".format(self.basename)
		elif os.path.exists(output_fitsfile):
			raise FileExistsError("{} has alaredy existed.".format(output_fitsfile))

		self.set_time_series()

		print(type(self.time_series_utc.unix))
		print(type(self.df['decisec']))
		self.time = np.array(self.time_series_utc.unix) + np.array(self.df['decisec']) /10000. 

		column_time = fits.Column(name='TIME',format='D', unit='sec', array=self.time)
		column_unixtime = fits.Column(name='unixtime',format='D', unit='sec', array=self.time_series_utc.unix)
		column_minute = fits.Column(name='minute',format='B', unit='minute', array=self.df['minute'])
		column_sec = fits.Column(name='sec',format='B', unit='sec', array=self.df['sec'])
		column_decisec = fits.Column(name='decisec',format='I', unit='100 microsec', array=self.df['decisec'])						
		column_pha = fits.Column(name='pha',format='I', unit='channel', array=self.df['pha'])

		column_defs = fits.ColDefs([column_time,column_unixtime,column_minute,column_sec,column_decisec,column_pha])
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

		hdu.header['comment'] = 'unixtime is UTC, while minute, sec, decisec columns and the file name are JST.'
		hdu.header['history'] = 'created at {} JST'.format(Time.now().to_datetime(tz_tokyo))
		hdu.writeto(output_fitsfile)

class ConfigFile():
	def __init__(self, file_path):
		self.file_path = file_path

		self.dict_keywords = {}
		if not os.path.exists(self.file_path):
			raise FileNotFoundError("{} not found".format(self.file_path))
		try:
			f = open(self.file_path)
			for line in f:
				keyword, value = line.split(',')
				if keyword == 'MULTIP':
					self.dict_keywords[keyword] = float(value)
				else:
					self.dict_keywords[keyword] = int(value)
			f.close()
		except OSError as e:
			raise

	def get_dict_keywords(self):
		return self.dict_keywords

##########################
# House Keeping File
##########################

class HouseKeepingFile(object):
	def __init__(self):
		self.nlines = 0
		self.file_path = None

	def show_data_summary(self):
		sys.stdout.write(str(self))

	def __str__(self):
		dump  = 'Format: {}'.format(self.format)		
		dump += 'Nlines: {}'.format(self.nlines)
		dump += '\n'
		return dump

class HousekeepingRawcsvFile():
	def __init__(self,file_path):
		self.file_path = file_path

		self.basename = os.path.splitext(os.path.basename(self.file_path))[0]

		if not os.path.exists(self.file_path):
			raise FileNotFoundError("{} not found".format(self.file_path))
		try:
			self.df = pd.read_csv(self.file_path, index_col=False, 
				names=['yyyymmdd','hhmmss','interval','rate1','rate2','rate3','rate4','rate5','rate6','temperature','pressure','humidity','differential','lux','gps_status','longitude','latitude'],
				dtype={'yyyymmdd':np.object,'hhmmss':np.object,'interval':np.int,'rate1':np.float64,'rate2':np.float64,'rate3':np.float64,'rate4':np.float64,'rate5':np.float64,'rate6':np.float64,'temperature':np.float64,'pressure':np.float64,'humidity':np.float64,'differential':np.float64,'lux':np.float64,'gps_status':np.int8,'longitude':np.float64,'latitude':np.float64})
			self.detid, self.yyyymmdd= self.basename.split('_')
		except OSError as e:
			raise

		self.format = 'rawcsv'
		self.nlines = len(self.df)

		self.set_filename_property()

	def set_filename_property(self):
		self.detid_str, self.yyyymmdd_jst = os.path.splitext(os.path.basename(self.file_path))[0].split("_")		

	def set_config_file(self,config_file):
		self.config = ConfigFile(config_file)

	def set_time_series(self):
		"""
		the standard unix time does not have enough accuracy below 1 second.
		Sub-second time stamp is handled by another column
		"""
		self.time_series_str  = np.char.array(self.df['yyyymmdd'] + 'T' + self.df['hhmmss'])
		time_series_jst = Time(self.time_series_str, format='isot', scale='utc', precision=5) 
		self.time_series_utc = time_series_jst - timedelta(hours=+9)

	def write_to_fitsfile(self,output_fitsfile=None,config_file=None):
		"""
		https://docs.astropy.org/en/stable/io/fits/usage/table.html
		"""
		sys.stdout.write('----- {} -----\n'.format(sys._getframe().f_code.co_name))

		if output_fitsfile == None:
			output_fitsfile = "{}_hk.fits".format(self.basename)
		elif os.path.exists(output_fitsfile):
			raise FileExistsError("{} has alaredy existed.".format(output_fitsfile))

		self.set_time_series()

		column_yyyymmdd = fits.Column(name='YYYYMMDD',format='10A', unit='JST', array=np.char.array(self.df['yyyymmdd']))
		column_hhmmss = fits.Column(name='HHMMSS',format='8A', unit='JST', array=np.char.array(self.df['hhmmss']))
		column_unixtime = fits.Column(name='Unixtime',format='D', unit='sec', array=self.time_series_utc.unix)
		column_interval = fits.Column(name='Interval',format='I', unit='sec', array=self.df['interval'])
		column_rate1 = fits.Column(name='Rate1',format='D', unit='count/s', array=self.df['rate1'])
		column_rate2 = fits.Column(name='Rate2',format='D', unit='count/s', array=self.df['rate2'])
		column_rate3 = fits.Column(name='Rate3',format='D', unit='count/s', array=self.df['rate3'])
		column_rate4 = fits.Column(name='Rate4',format='D', unit='count/s', array=self.df['rate4'])
		column_rate5 = fits.Column(name='Rate5',format='D', unit='count/s', array=self.df['rate5'])								
		column_rate6 = fits.Column(name='Rate6',format='D', unit='count/s', array=self.df['rate6'])	
		column_temperature = fits.Column(name='Temperature',format='D', unit='degC', array=self.df['temperature'])		
		column_pressure = fits.Column(name='Pressure',format='D', unit='hPa', array=self.df['pressure'])					
		column_humidity = fits.Column(name='Humidity',format='D', unit='%', array=self.df['humidity'])	
		column_differential = fits.Column(name='Differential',format='D', unit='count/s', array=self.df['differential'])
		column_lux = fits.Column(name='Illumination',format='D', unit='lux', array=self.df['lux'])	
		column_gps_status = fits.Column(name='Gps_status',format='I', unit='', array=self.df['gps_status'])	
		column_longitude = fits.Column(name='Longitude',format='D', unit='deg', array=self.df['longitude'])		
		column_latitude = fits.Column(name='Latitude',format='D', unit='deg', array=self.df['latitude'])			

		column_defs = fits.ColDefs([column_yyyymmdd,column_hhmmss,column_unixtime,column_interval,column_rate1,column_rate2,column_rate3,column_rate4,column_rate5,column_rate6,column_temperature,column_pressure,column_humidity,column_differential,column_lux,column_gps_status,column_longitude,column_latitude])
		hdu = fits.BinTableHDU.from_columns(column_defs,name='HK')

		dict_keywords = {
			'DET_ID':[self.detid_str,'Detector_ID'],
			'YYYYMMDD':[self.yyyymmdd_jst,'Year, month, and day in JST of the file']}
		for keyword in dict_keywords.keys():
			hdu.header[keyword] = dict_keywords[keyword][0]
			hdu.header.comments[keyword] = dict_keywords[keyword][1]

		if config_file != None:
			self.set_config_file(config_file)
			for keyword in self.config.dict_keywords.keys():
				hdu.header[keyword] = self.config.dict_keywords[keyword]

		hdu.header['comment'] = 'unixtime is UTC, while yyyymmddTHH:MM:SS column and the file name are JST.'
		hdu.header['history'] = 'created at {} JST'.format(Time.now().to_datetime(tz_tokyo))
		hdu.writeto(output_fitsfile)

class HousekeepingRemoteFile():
	def __init__(self,file_path):
		sys.stdout.write('----- HousekeepingRemoteFile -----\n')

		self.file_path = file_path

		self.basename = os.path.splitext(os.path.basename(self.file_path))[0]

		if not os.path.exists(self.file_path):
			raise FileNotFoundError("{} not found".format(self.file_path))
		try:
			self.df = pd.read_csv(self.file_path, index_col=False)
		except OSError as e:
			raise
		yyyymmdd_hhmmss = self.df['time'].str.split(" ",n=1,expand=True)
		self.df['yyyymmdd'] = yyyymmdd_hhmmss[0]
		self.df['hhmmss'] = yyyymmdd_hhmmss[1]

		self.format = 'remotecsv'
		self.nlines = len(self.df)

		self.set_filename_property()

	def set_filename_property(self):
		self.detid_str = os.path.basename(self.file_path).split('_')[0]

		starttime_str = os.path.basename(self.file_path)[11:24]
		self.starttime_str = '20'+starttime_str[0:2]+'-'+starttime_str[2:4]+'-'+starttime_str[4:7]
		self.starttime_str += starttime_str[7:9] + ':' + starttime_str[9:11] + ':' + starttime_str[11:13]

		stoptime_str = os.path.basename(self.file_path)[25:38]
		self.stoptime_str = '20'+stoptime_str[0:2]+'-'+stoptime_str[2:4]+'-'+stoptime_str[4:7]
		self.stoptime_str += stoptime_str[7:9] + ':' + stoptime_str[9:11] + ':' + stoptime_str[11:13]

		self.detid_str = os.path.basename(self.file_path)[3:6]

	def set_time_series(self):
		"""
		the standard unix time does not have enough accuracy below 1 second.
		Sub-second time stamp is handled by another column
		"""
		self.time_series_str  = np.char.array(self.df['yyyymmdd'] + 'T' + self.df['hhmmss'])
		time_series_jst = Time(self.time_series_str, format='isot', scale='utc', precision=5) 
		self.time_series_utc = time_series_jst - timedelta(hours=+9)
		self.df['interval'] = np.insert(np.diff(self.time_series_utc.unix),0,np.nan)

	def write_to_fitsfile(self,output_fitsfile=None):
		"""
		https://docs.astropy.org/en/stable/io/fits/usage/table.html
		"""
		sys.stdout.write('----- {} -----\n'.format(sys._getframe().f_code.co_name))

		if output_fitsfile == None:
			output_fitsfile = os.path.splitext(os.path.basename(self.file_path))[0] + '.fits'
		elif os.path.exists(output_fitsfile):
			raise FileExistsError("{} has alaredy existed.".format(output_fitsfile))

		self.set_time_series()

		column_yyyymmdd = fits.Column(name='YYYYMMDD',format='10A', unit='JST', array=np.char.array(self.df['yyyymmdd']))
		column_hhmmss = fits.Column(name='HHMMSS',format='8A', unit='JST', array=np.char.array(self.df['hhmmss']))
		column_unixtime = fits.Column(name='Unixtime',format='D', unit='sec', array=self.time_series_utc.unix)
		column_interval = fits.Column(name='Interval',format='I', unit='sec', array=self.df['interval'])
		column_rate1 = fits.Column(name='Rate1',format='D', unit='count/s', array=self.df['area1'])
		column_rate2 = fits.Column(name='Rate2',format='D', unit='count/s', array=self.df['area2'])
		column_rate3 = fits.Column(name='Rate3',format='D', unit='count/s', array=self.df['area3'])
		column_rate4 = fits.Column(name='Rate4',format='D', unit='count/s', array=self.df['area4'])
		column_rate5 = fits.Column(name='Rate5',format='D', unit='count/s', array=self.df['area5'])								
		column_rate6 = fits.Column(name='Rate6',format='D', unit='count/s', array=self.df['area6'])	
		column_temperature = fits.Column(name='Temperature',format='D', unit='degC', array=self.df['temp'])		
		column_pressure = fits.Column(name='Pressure',format='D', unit='hPa', array=self.df['pressure'])					
		column_humidity = fits.Column(name='Humidity',format='D', unit='%', array=self.df['humidity'])	
		column_differential = fits.Column(name='Differential',format='D', unit='count/s', array=self.df['differential'])
		column_lux = fits.Column(name='Illumination',format='D', unit='lux', array=self.df['lux'])	
		column_gps_status = fits.Column(name='Gps_status',format='I', unit='', array=self.df['gps_status'])	
		column_longitude = fits.Column(name='Longitude',format='D', unit='deg', array=self.df['longitude'])		
		column_latitude = fits.Column(name='Latitude',format='D', unit='deg', array=self.df['latitude'])			

		column_defs = fits.ColDefs([column_yyyymmdd,column_hhmmss,column_unixtime,column_interval,column_rate1,column_rate2,column_rate3,column_rate4,column_rate5,column_rate6,column_temperature,column_pressure,column_humidity,column_differential,column_lux,column_gps_status,column_longitude,column_latitude])
		hdu = fits.BinTableHDU.from_columns(column_defs,name='HK')

		dict_keywords = {
			'DET_ID':[self.detid_str,'Detector_ID'],
			'INTERVAL':[int(np.mean(self.df['interval'][1:-1])),'Interval (sec)'],
			'AREABD1':[0.0,'Not defined.'],
			'AREABD2':[0.0,'Not defined.'],
			'AREABD3':[0.0,'Not defined.'],
			'AREABD4':[0.0,'Not defined.'],
			'AREABD5':[0.0,'Not defined.'],									
			'AREABD6':[0.0,'Not defined.']}
		for keyword in dict_keywords.keys():
			hdu.header[keyword] = dict_keywords[keyword][0]
			hdu.header.comments[keyword] = dict_keywords[keyword][1]

		#if config_file != None:
		#	self.set_config_file(config_file)
		#	for keyword in self.config.dict_keywords.keys():
		#		hdu.header[keyword] = self.config.dict_keywords[keyword]

		hdu.header['comment'] = 'unixtime is UTC, while yyyymmddTHH:MM:SS column and the file name are JST.'
		hdu.header['history'] = 'created at {} JST'.format(Time.now().to_datetime(tz_tokyo))
		hdu.writeto(output_fitsfile)

class HousekeepingFitsFile():
	def __init__(self,file_path):
		self.file_path = file_path

		self.basename = os.path.splitext(os.path.basename(self.file_path))[0]

		if not os.path.exists(self.file_path):
			raise FileNotFoundError("{} not found".format(self.file_path))
		try:
			self.hdu = fits.open(self.file_path)
		except OSError as e:
			raise

		self.format = 'fits'
		self.nlines = len(self.hdu['HK'].data)

	def plot(self):
		data = self.hdu['HK'].data

		time_series_utc = Time(data['Unixtime'],format='unix',scale='utc')
		time_series_jst = time_series_utc.to_datetime(timezone=tz_tokyo)
		matplotlib.rcParams['timezone'] = 'Asia/Tokyo'

		title  = 'DET_ID=%s ' % self.hdu['HK'].header['DET_ID']
		title += '(Longitude=%.3f deg, ' % (np.mean(data['Longitude']))
		title += 'Latitude=%.3f deg)' % (np.mean(data['Latitude']))		
		title += '\n'
		title += '%s ' % str(time_series_jst[0])[0:10]
		title += 'Interval=%d min ' % (self.hdu['HK'].header['INTERVAL'])
		title += '(%s)' % os.path.basename(self.file_path)
		title += '\n'		
		if self.hdu['HK'].header['AREABD2'] > 0.0:
			title += 'Rate L (1+2):<%.1f MeV, ' % (self.hdu['HK'].header['AREABD2']/1000.0)
			title += 'Rate M (3+4):%.1f-%.1f MeV, ' % (self.hdu['HK'].header['AREABD2']/1000.0,self.hdu['HK'].header['AREABD4']/1000.0)		
			title += 'Rate H (5+6):>%.1f MeV, ' % (self.hdu['HK'].header['AREABD4']/1000.0)

		outpdf = '%s.pdf' % self.basename

		fig, axs = plt.subplots(9,1, figsize=(8.27,11.69), 
			sharex=True, gridspec_kw={'hspace': 0})
		axs[0].step(time_series_jst,data['Rate1']+data['Rate2'],'o-', mec='k', markersize=2,where='mid')
		axs[0].set_ylabel(r"Rate L (cps)")
		axs[0].set_title(title)	
		axs[1].step(time_series_jst,data['Rate3']+data['Rate4'],'o-', mec='k', markersize=2,where='mid')
		axs[1].set_ylabel(r"Rate M (cps)")	
		axs[2].step(time_series_jst,data['Rate5']+data['Rate6'],'o-', mec='k', markersize=2,where='mid')
		axs[2].set_ylabel(r"Rate H (cps)")				
		axs[3].step(time_series_jst,data['Temperature'],where='mid')
		axs[3].set_ylabel(r"Temp. (degC)")
		axs[4].step(time_series_jst,data['Pressure'],where='mid')
		axs[4].set_ylabel(r"Press. (hPa)")		
		axs[5].step(time_series_jst,data['Humidity'],where='mid')
		axs[5].set_ylabel(r"Humid. (%)")
		axs[6].step(time_series_jst,data['Differential'],where='mid')		
		axs[6].set_ylabel(r"Diff (cps)")	
		axs[6].set_yscale('log')		
		axs[7].step(time_series_jst,data['Illumination'],where='mid')		
		axs[7].set_yscale('log')
		axs[7].set_ylabel(r"Illum. (lux)")
		axs[8].step(time_series_jst,data['Gps_status'],where='mid')		
		axs[8].set_ylabel(r"GPS status")		
		axs[8].set_xlabel(r"Time (JST)")
		axs[8].set_ylim(-0.5,2.5)
		axs[8].xaxis.set_major_formatter(dates.DateFormatter('%m-%d\n%H:%M'))
		
		axs[8].set_xlim(time_series_jst[0],time_series_jst[-1])
		for ax in axs:
			ax.label_outer()	
			ax.minorticks_on()
			ax.xaxis.grid(True)
			ax.xaxis.grid(which='major', linestyle='--', color='#000000')
			ax.xaxis.grid(which='minor', linestyle='-.')	
			ax.xaxis.set_minor_locator(dates.HourLocator())
			ax.tick_params(axis="both", which='major', direction='in', length=5)
			ax.tick_params(axis="both", which='minor', direction='in', length=3)			
		fig.align_ylabels(axs)
		plt.tight_layout(pad=2)
		plt.rcParams["font.family"] = "serif"
		plt.rcParams["mathtext.fontset"] = "dejavuserif"		
		plt.savefig(outpdf)

def fopen(file_path):
	if re.fullmatch(r'\d{3}_\d{8}_\d{2}.csv', os.path.basename(file_path)):
		return EventRawcsvFile(file_path)
	elif re.fullmatch(r'\d{3}_\d{8}_\d{2}.evt', os.path.basename(file_path)):
		return EventFitsFile(file_path)
	elif re.fullmatch(r'\d{3}_\d{8}.csv', os.path.basename(file_path)):
		return HousekeepingRawcsvFile(file_path)	
	elif re.fullmatch(r'\d{3}_\d{8}_hk.fits', os.path.basename(file_path)):
		return HousekeepingFitsFile(file_path)	
	elif re.fullmatch(r'cgm\d{3}_rhk_\d{6}T\d{6}_\d{6}T\d{6}.csv',os.path.basename(file_path)):
		return HousekeepingRemoteFile(file_path)
	elif re.fullmatch(r'cgm\d{3}_rhk_\d{6}T\d{6}_\d{6}T\d{6}.fits',os.path.basename(file_path)):
		return HousekeepingFitsFile(file_path)					
	else:
		raise NotImplementedError("EventFile class for this file type is not implemented")		

