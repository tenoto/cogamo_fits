# cogamo 

[![hackmd-github-sync-badge](https://hackmd.io/BUiCqBFqQDeVTWameMicjw/badge)](https://hackmd.io/BUiCqBFqQDeVTWameMicjw)

Analysis package for the Compact Gamma-ray Monitor (CoGamo) of the "Thundercloud Project" organized by the GROWTH Collaboration. 

This page summarizes the beta-version prototype of an analyses package. 

## Installation and setup

For your first installation, use the git clone command.
```
git clone https://github.com/tenoto/cogamo.git
```

Then, under the top directory of  the "cogamo" library,
```
source setenv/setenv.bashrc
```

## Raw data format

### House Keeping (HK) data 
House Keeping (HK) data includes 


## Examples

### House Keeping (HK) data 

At our analysis pipeline, we convert all the raw csv-format files to fits-format files. This conversion is useful because the fits-format files can include header keywords in a single file and becase we can utilize the HEASoft and the astropy python library.

Example scripts and test files are included in "tests/*.sh" and "tests/data" directories, respectively. 

Let us convert the raw csv-format HK files to fits files: run the command "tests/test_cgm_convert_hkfile_to_fitsfile.sh", which explicit description is
```
cogamo/cli/cgm_convert_hkfile_to_fitsfile.py tests/data/011_20200305.csv -c tests/data/config.csv
```

Here ``-c`` option attachs parameters described in the config.csv file into header keywords in the output fitsfile (011_20200305_hk.fits). 

The structure of the output fits file (011_20200305_13.evt) can be checked via the HEASoft "fstruct:" command.

```
  No. Type     EXTNAME      BITPIX Dimensions(columns)      PCOUNT  GCOUNT
 
   0  PRIMARY                  8     0                           0    1
   1  BINTABLE HK              8     134(18) 288                 0    1
 
      Column Name                Format     Dims       Units     TLMIN  TLMAX
      1 YYYYMMDD                   10A                 JST
      2 HHMMSS                     8A                  JST
      3 Unixtime                   D                   sec
      4 Interval                   I                   sec
      5 Rate1                      D                   count/s
      6 Rate2                      D                   count/s
      7 Rate3                      D                   count/s
      8 Rate4                      D                   count/s
      9 Rate5                      D                   count/s
     10 Rate6                      D                   count/s
     11 Temperature                D                   degC
     12 Pressure                   D                   hPa
     13 Humidity                   D                   %
     14 Differential               D                   count/s
     15 Illumination               D                   lux
     16 Gps_status                 I
     17 Longitude                  D                   deg
     18 Latitude                   D                   deg
```     

Then, you can make a plot of curves of parameters command (as a script "tests/test_cgm_plot_hkfile.sh"):

```
cogamo/cli/cgm_plot_hkfile.py 011_20200305_hk.fits
```

![](https://i.imgur.com/XjVjnM4.jpg)

### Event data 

We can also convert the csv-format event file into a fits-format file:``tests/test_cgm_convert_rawcsv_evtfile_to_fitsfile.sh``, which explicit description is 

```
cogamo/cli/cgm_convert_rawcsv_evtfile_to_fitsfile.py tests/data/011_20200305_13.csv -c tests/data/config.csv
```

In the same way as the HK data, the ``-c`` option is usded to attach the config file parameters. 

The output fits file format is:

```
  No. Type     EXTNAME      BITPIX Dimensions(columns)      PCOUNT  GCOUNT
 
   0  PRIMARY                  8     0                           0    1
   1  BINTABLE EVENTS          8     14(5) 670841                0    1
 
      Column Name                Format     Dims       Units     TLMIN  TLMAX
      1 unixtime                   D                   sec
      2 minute                     B                   minute
      3 sec                        B                   sec
      4 decisec                    I                   100 microsec
      5 pha                        I                   channel
```      

Then, we can plot a histogram of the "pha" parameter: run "tests/test_cgm_plot_pha.sh", which is

```
cogamo/cli/cgm_plot_pha.py 011_20200305_13.evt
```

![](https://i.imgur.com/QUuZlQE.jpg)

As of August 15, 2020, functions to handle event files are tentative example, which should be developed later. 

## Change History

- 2020-08-15 The initial version (T.Enoto)