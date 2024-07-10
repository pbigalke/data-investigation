
# %%
import pandas as pd
import xarray as xr
from datetime import datetime
import glob
import sys
sys.path.append("..")

import helpers.helper_conversions as hlp

# %%
def read(file_path):
    """ read processed MWCC-H output containing probability of hail
    """
    with xr.open_dataset(file_path) as dataset:
        return dataset

def get_y_m_d_from_filepath(file_path):
    
    return None


def get_mwcch_files_in_study_period(mwcch_directory, detectors, years, months=None, days=None):
    
    if detectors is not None and not isinstance(detectors, list):
        detectors = list(detectors)
    if years is not None and not isinstance(years, list):
        years = list(years)
    if months is not None and not isinstance(months, list):
        months = list(months)
    if days is not None and not isinstance(days, list):
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

def get_mwcch_file_at_msg_timestamp(mwcch_directory, detectors, timestamp, msg_res=15):

    dt = hlp.get_datestring_from_npdatetime(timestamp)

    mwcch_files = []
    for f in glob.glob(f"{mwcch_directory}/{dt[:4]}/{dt[4:6]}/{dt[6:8]}/{dt[:8]}*_E{dt[9:11]}*.nc"):
        
        if f.split('_')[-1].split('.')[0] in detectors:
            start_msg = int(dt[-4:])
            end_msg = start_msg + msg_res if (int(dt[-2:])+msg_res) < 60 else start_msg + (40+msg_res)
            start_mwcch = int(f.split('_')[-3][1:])
            end_mwcch = int(f.split('_')[-2][1:])
            if start_msg < start_mwcch and start_mwcch < end_msg \
                or start_msg < end_mwcch and end_mwcch < end_msg:
                print("msg start, end ", start_msg, end_msg)
                print("mwcch start, end ", start_mwcch, end_mwcch) 
                print()
                mwcch_files.append(f)

    return mwcch_files



# %%
if __name__ == '__main__':
    import numpy as np
    # test on exaple file
    example_file = "mhs_METOPB_20230724-S1905-E2046_056289"
    satellite = 'METOPB'
    
    path = "/net/merisi/pbigalke/data/MWCC-H/netcdf"
    years = [2022]
    months = [6]
    days = [5]
    detectors = ["ATMS", "MHS", "SSMIS"]
    all_files = get_mwcch_files_in_study_period(path, detectors, years, months, days)
    for f in all_files:
        print(f)

# %%
