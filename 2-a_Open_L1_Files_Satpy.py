"""
Open L1 Files of FY_4A satellite over Vietnam Area 
data quality control and projection

author: Daniele Corradini
last Edit: June 2023
"""

##################
#import libraries#
##################

import numpy as np
import pandas as pd
import satpy 
from glob import glob
import xarray as xr
import datetime
import sys
import os


#############
#check Satpy#
#############

#check if satpy has all the dependencies installed
#from satpy.utils import check_satpy
#check_satpy()

#check the readers name available in satpy
#print(satpy.available_readers())


##############
#define paths#
##############

# Get the path of the current working directory
cwd = os.getcwd().split('/')[1]

if cwd == 'home':
    # Define the file path 
    path_to_file = "/home/daniele/Documenti/EarthPhysics/Thesis/data/FY_4A/L1/"
    
    #import customized methods
    sys.path.append('/home/daniele/Documenti/EarthPhysics/Thesis/data/FY_4A/')
    from Functions import Data_Preprocessing_Functions 

    
else:
    #path to files
    path_to_file = "/Dati/william.cossich/indra/FY_4A/L1/"

    #import customized methods
    sys.path.append('/Dati/william.cossich/indra/')
    from FY_4A import Data_Preprocessing_Functions 
    


#open all files in directory 
h5file = "FY4A-_AGRI--_N_DISK_1047E_L1-_FDI-_MULT_NOM_*_4000M_V0001.HDF"

#if I want to consider just hourly resolution try to open files with
#h5file = 'FY4A-_AGRI--_N_DISK_1047E_L1-_FDI-_MULT_NOM_*00000_*_4000M_V0001.HDF'

#test code with a single file
#h5file = "FY4A-_AGRI--_N_DISK_1047E_L1-_FDI-_MULT_NOM_20201001024500_20201001025959_4000M_V0001.HDF"

fnames = glob(path_to_file+h5file)


###############
#Quality Check#
###############

#check if all files were downloaded
n_miss_files = Data_Preprocessing_Functions.check_missing_download(path_to_file,'L1_OrderFileList.txt',fnames)
print('Number of files that failed to be downloaded:',n_miss_files)

#check for corrupted files
not_corrupted_files = Data_Preprocessing_Functions.check_openable_files(path_to_file,fnames,'agri_fy4a_l1')
print('Number of files that are corrupted:', len(fnames)-len(not_corrupted_files))

#check for missing time steps
missing_intervals = Data_Preprocessing_Functions.check_file_coverage(path_to_file, fnames,'202010010000','202010312359')
print('Number of missing intervals:', len(missing_intervals))
#[99.7311828  33.19892473  0.         33.19892473]

###########
#Open Data#
###########

open_data = True

if open_data:

    #Vietnam Area
    lonmin, latmin, lonmax, latmax= 101, 7, 110, 24

    #check for nan values, inizialize array
    nan_values = []
    start_nan = []
    end_nan = []

    #Read data at different temporal steps
    for t,f in enumerate(not_corrupted_files):
        file = f.split('/')[-1]
        print(file)

        #get start and end time from filename format yyyymmddhhmmss
        start_time = file.split('_')[9]
        end_time = file.split('_')[10]

        #append date for nan checking
        start_nan.append(datetime.datetime.strptime(start_time, "%Y%m%d%H%M%S"))
        end_nan.append(datetime.datetime.strptime(end_time, "%Y%m%d%H%M%S"))
        
        #open file with Satpy
        scn = satpy.Scene(reader='agri_fy4a_l1', filenames=[f]) #By default bad quality scan lines are masked and replaced with np.nan based on the quality flags provided by the data 
        
        #get the channel names
        channels = scn.available_dataset_names()  

        #inizialize list for nan values for each channel
        nan_channels = []

        #get the lat/lon coords

        #Load one channel
        scn.load(['C01'])       

        #Crop to Vietnam area
        crop_scn = scn.crop(ll_bbox=(lonmin, latmin, lonmax, latmax))

        #get coord in the cropped area
        area_crop = crop_scn['C01'].attrs['area'] #area in m
        sat_lon_crop, sat_lat_crop = area_crop.get_lonlats() #lat/lon grid (438,246)

        # create DataArrays with the coordinates using cloud mask grid
        lon_da = xr.DataArray(sat_lon_crop, dims=("y", "x"), name="lon grid")
        lat_da = xr.DataArray(sat_lat_crop, dims=("y", "x"), name="lat grid")

        # combine DataArrays into xarray object
        ds = xr.Dataset({"lon grid": lon_da, "lat grid": lat_da})

        #loop over the channels #1-6 reflectance; 7-14 TB -> reflectance only for shortwave
        #TODO channels loop can be parallelized as the order is not important, use dask or multiporcessing 
        for ch in channels:
            #Load channel
            scn.load([ch])       

            #Crop to Vietnam area
            crop_scn = scn.crop(ll_bbox=(lonmin, latmin, lonmax, latmax))

            #get data in the cropped area
            sat_data_crop = crop_scn[ch].values #R/Tb

            #check grid
            #print(Data_Preprocessing_Functions.check_regular_grid(sat_lon_crop,sat_lat_crop,'lat',True))
            #print(Data_Preprocessing_Functions.check_regular_grid(sat_lon_crop,sat_lat_crop,'lon',True))
        
            #check for missing data
            nan_channels.append(np.sum(np.isnan(sat_data_crop))/len(sat_data_crop)) #take the ratio of nan and the total number of pixels
            
            #add channel values to the Dataset
            sat_da = xr.DataArray(sat_data_crop, dims=("y", "x"), name="channel value "+str(ch))
            ds["channel value "+str(ch)] = sat_da

        #append the list of nan values for all the channels
        nan_values.append(nan_channels)

        # Add a new dimension for the start time coordinate
        ds = ds.expand_dims('Start Time', axis=0)
        ds['Start Time'] = [start_time]

        # Set the directory path to save files
        proj_file_path = path_to_file+'L1_reprojected/'

        # Check if the directory exists
        if not os.path.exists(proj_file_path):
            # Create the directory if it doesn't exist
            os.makedirs(proj_file_path)

        #save the features using a similar name of the HDF5 file but in netCDF format
        ds.to_netcdf(proj_file_path+f.split('/')[-1].split('.')[0]+'.nc')
        print('Projected L1 product saved\n')
        
        #print(ds)

          
    ######################
    #check missing values#
    ######################

    #convert to dataframe table the nan lists
    df_nan = pd.DataFrame(nan_values, columns=channels)

    #add times
    df_nan['Start Time'] = start_nan
    df_nan['End Time'] = end_nan

    #save to csv file
    df_nan.to_csv(path_to_file+'nan_ratio.csv', index=False)
    
    #df_nan = pd.read_csv(path_to_file+'nan_ratio.csv')

    #plot number of nan values (ratio) for each channel and time step
    Data_Preprocessing_Functions.plot_nan_ratio(df_nan,path_to_file) 
