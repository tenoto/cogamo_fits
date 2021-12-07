# cogamo_fits

(obsolete on 2021-12-07, will be merged to cogamo)

[![hackmd-github-sync-badge](https://hackmd.io/BUiCqBFqQDeVTWameMicjw/badge)](https://hackmd.io/BUiCqBFqQDeVTWameMicjw)

Analysis package for the Compact Gamma-ray Monitor (Coamo) of the "Thundercloud Project" organized by the GROWTH Collaboration. 

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

All the measured data are recorded in a MicroSD card of the Cogamo detector. 

### Directory structure
The cogamo data are organized in the order of detector IDs (Det_ID). In the following case, the Det_ID 11 has "config.csv", "data", and "log" directories. 
```
011
├── config.csv
├── data
│   ├── 011_20200305_00.csv
│   ├── 011_20200305_01.csv
...
│   └── 011_20200305_23.csv
└── log
    ├── 011_20181002.csv
    ├── 011_20181031.csv
...
```
The "data" folder includes the event data, while the "log" folder include the house keeping (HK) data.

### House Keeping (HK) data 
The House Keeping (HK) data file includes basic parameters of a detector and its environment. The file name is 

```
[det_id]_[yyyymmdd].csv
```

where the time is defined in JST. The file is generated per a day.

The raw csv-format file is included the following columns (',' separated):

1. yyyy-mm-dd (JST)
2. HH:MM:SS (JST)
3. data recording interval (min)
4. rate1 (cps) below "AREABD1" of " config.csv"
5. rate2 (cps) between "AREABD1" and  "AREABD2" of " config.csv"
6. rate3 (cps) between "AREABD2" and  "AREABD3" of " config.csv"
7. rate4 (cps) between "AREABD3" and  "AREABD4" of " config.csv"
8. rate5 (cps) between "AREABD4" and  "AREABD5" of " config.csv"
9. rate6 (cps) above "AREABD5" of " config.csv"
10. temperature (degC)
11. pressure (hPa)
12. humidity (%)
13. the maximum value among the difference of 10-sec moving average of count rates to the latest count rates (10秒移動平均とCPS値との差の最大値:定義を確認する必要がある) 
14. optical illumination (lux)
15. gps status (0:invalid, 1 or 2: valid)
16. longitude (deg)
17. latitude (deg)


### Event data 
The event data file recorded all the individual radiation events. The file name is 

```
[det_id]_[yyyymmdd]_[hour].csv
```

where the time is defined in JST.

The event data file include the following columns:



1. minute
2. sec
3. 1/10000 sec
4. ADC channel (pha: pulse height amplitude) [0-1023]

### Config file
The config file is incldued in a MicroSD card of the Cogamo detector, which setup the instrumental parameters

- INTERVAL,5 (*Internal for writing of the HK data*)
- ID,100 (*Detector ID*)
- AREABD1,1600 (*Threshold energy between rate1 and rate2 in a keV unit (i.e., 1600 keV)*)
- AREABD2,3000 (*Threshold energy between rate2 and rate3 in a keV unit (i.e., 3000 keV)*)
- AREABD3,5000 
- AREABD4,8000 
- AREABD5,10000 
- TIMECONS,10 (*Not used, same in the following parameters*)
- SPCTRINT,120 
- MODE,0 
- NBIN,60 
- MULTIP,1.5 
- NPRE,200 
- RTH,300 
- RBACK,280

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

## Time series

The original time stamps are defined in Japan Standard Time (JST, UTC
+9 hours), calibrated by GPS signals. 

The filenames of the HK and event files, columns "YYYYMMDD", "HHMMSS" of the HK file, "minute", "sec", "decisec" of the event file are defined as the JST in the same way as the raw csv formt. 

On the other hand, "unixtime" of the HK and event files are converted to the astropy Time object defined in the UTC scale. 

## Sample data 

[sample data](https://riken-share.box.com/s/p97ssaj5d857dk6ysg8lldyxbedswths)

Intersting data:
- 2020-03-05 Det_ID=011 (short burst = photonuclear reaction at lightnin)
- 2018-12-17 Det_ID=019 (long burst = gamma-ray glow)

## Online viwer

[online viewer](http://www.tacinc2.sakura.ne.jp/GROWTH_8/index.php)

## Change History

- 2020-08-15 The initial version (T.Enoto)
