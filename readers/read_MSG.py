# %%
import xarray as xr
import os
import sys
sys.path.append('..')
import helpers.datetime_helper as hlp

MSG_PATH = "/data/sat/msg/netcdf/parallax"

CHANNELS = ["IR_016", "IR_039", "IR_087", "IR_097", "IR_108", "IR_120", "IR_134",
            "VIS006", "VIS008", "WV_062", "WV_073"]

# %%
def read(msg_file, channels=None):

    drop = [ch for ch in CHANNELS if ch not in channels] if channels is not None else None
    with xr.open_dataset(msg_file, drop_variables=drop) as dataset:
        return dataset

def get_y_m_d_from_filepath(msg_file):
    name = os.path.basename(msg_file)
    date = name.split('_')[0]
    return date[:4], date[4:6], date[6:]

def get_lon_lat():
    MSG_example_file = f"{MSG_PATH}/2023/09/20230930-EXPATS-RG.nc"
    with xr.open_dataset(MSG_example_file, drop_variables=CHANNELS) as dataset:
        lon = dataset.lon.values
        lat = dataset.lat.values
    return lon, lat

def get_MSG_files_from_timestamps(msg_dt):
    # check if input is list
    if not isinstance(msg_dt, list):
        msg_dt = [msg_dt]
    
    msg_files = []
    # loop over timestamps and get corresponding MSG file
    for dt in msg_dt:
        # convert to string
        dt_str = hlp.get_datestring_from_npdatetime(dt)

        # get corresponding MSG file containing this timestamp
        msg_files.append(f"{MSG_PATH}/{dt_str[:4]}/{dt_str[4:6]}/{dt_str}-EXPATS-RG.nc") #20220615-EXPATS-RG.nc
    
    return msg_files

