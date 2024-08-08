# %%
import xarray as xr
import os

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
