import glob
import os
import numpy as np
import sys
sys.path.append("..")
import helpers.helper_conversions as hlp

def get_mwcch_files_in_study_period(mwcch_directory, detectors, years, months=None, days=None):
    
    if detectors is not None and not isinstance(detectors, list):
        detectors = list(detectors)
    if years is not None and not isinstance(years, list):
        years = list(years)
    if months is None:
        months = np.arange(1, 13, 1)
    else:
        if not isinstance(months, list):
            months = list(months)
    if days is None:
        days = np.arange(1, 32, 1)
    else:
        if not isinstance(days, list):
            days = list(days)

    mwcch_files = []

    for year in years:
        for month in months:
            for day in days:
                for f in glob.glob(f"{mwcch_directory}/{year}/{month:02}/{day:02}/*.nc"):
                    for detector in detectors:
                        if detector in f:
                            mwcch_files.append(f)

    return mwcch_files

def get_files_in_study_period(directory, years, months=None, days=None):
    
    if years is not None and not isinstance(years, list):
        years = list(years)
    if months is None:
        months = np.arange(1, 13, 1)
    else:
        if not isinstance(months, list):
            months = list(months)
    if days is None:
        days = np.arange(1, 32, 1)
    else:
        if not isinstance(days, list):
            days = list(days)

    all_files = []

    for year in years:
        for month in months:
            for day in days:
                path_day = f"{directory}/{year}/{month:02}/{day:02}"
                if os.path.exists(path_day):
                    for f in glob.glob(f"{path_day}/*.nc"):
                        all_files.append(f)

    return all_files

def get_msg_daily_files_in_study_period(directory, years, months=None, days=None):
    
    if years is not None and not isinstance(years, list):
        years = list(years)
    if months is None:
        months = np.arange(1, 13, 1)
    else:
        if not isinstance(months, list):
            months = list(months)
    if days is None:
        days = np.arange(1, 32, 1)
    else:
        if not isinstance(days, list):
            days = list(days)

    all_files = []

    for year in years:
        for month in months:
            path_month = f"{directory}/{year}/{month:02}"
            if os.path.exists(path_month):
                for day in days:
                    for f in glob.glob(f"{path_month}/{year}{month:02}{day:02}-EXPATS-RG.nc"):
                        all_files.append(f)

    return all_files

def get_file_at_msg_timestamp(directory, timestamp, msg_res=15):

    dt = hlp.get_datetimestring_from_npdatetime(timestamp)

    # read in all files in directory that are close to timestamp
    files_to_check = glob.glob(f"{directory}/{dt[:4]}/{dt[4:6]}/{dt[6:8]}/{dt[:8]}*_E{dt[9:11]}*.nc")

    closest_files = []
    for f in files_to_check:
        start_msg = int(dt[-4:])
        end_msg = start_msg + msg_res if (int(dt[-2:])+msg_res) < 60 else start_msg + (40+msg_res)
        start_data = int(f.split('_')[-4][1:])
        end_data = int(f.split('_')[-3][1:])
        if start_msg < start_data and start_data < end_msg \
            or start_msg < end_data and end_data < end_msg:
            closest_files.append(f)

    return closest_files

def get_closest_msg_files(directory, timestamp, msg_res=15):

    dt = hlp.get_datestring_from_npdatetime(timestamp)

    closest_files = []
    # TODO: find closest MSG timestamp to given timestamp
   
    return closest_files


