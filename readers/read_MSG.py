# %%
import xarray as xr

# %%
def read(msg_file):
    with xr.open_dataset(msg_file) as dataset:
            return dataset

# %%
