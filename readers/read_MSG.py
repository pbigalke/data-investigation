# %%
import glob
import xarray as xr
import sys
from datetime import datetime
sys.path.append("..")
# import my own script
import helpers.helper_conversions as hlp

# %%
def get_MSG_files_in_study_period(msg_directory, years, months, days):

    if years is not None and not isinstance(years, list):
        years = list(years)
    if months is not None and not isinstance(months, list):
        months = list(months)
    if days is not None and not isinstance(days, list):
        days = list(days)

    msg_files = []

    for year in years:
        for month in months:
            for day in days:
                for f in glob.glob(f"{msg_directory}/{year}/{month:02}/{year}{month:02}{day:02}-EXPATS-RG.nc"):
                    msg_files.append(f)

    return msg_files

def read(msg_file):
    with xr.open_dataset(msg_file) as dataset:
            return dataset

# %% 
if __name__ == '__main__':
    path = "/data/sat/msg/netcdf/parallax"
    years = [2022]
    months = [6]
    days = [5]
    get_MSG_files_in_study_period(path, years, months, days)
# %%
