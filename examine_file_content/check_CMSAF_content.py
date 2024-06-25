# %%
import xarray as xr
import glob

path = "/net/merisi/pbigalke/data/CMSAF_SSMIS"

example_files = sorted(glob.glob(f"{path}/*.nc"))
example_file = f"{path}/BTRin20220605000000424SSF18E1GL.nc"

with xr.open_dataset(example_file, group='scene_uas') as data:
    print(data.scene_channel.values + 1)

# %%
from netCDF4 import Dataset
rootgrp = Dataset(example_file, "r")
print(rootgrp.groups)

# %%
for f in example_files:
    with xr.open_dataset(f, group='scene_las') as data:
        print(f)
        print(data)
        continue
        for coord in data.keys():
            print(coord)


# %%
for k in data.keys():
    print("-------", k)
    print(data[k])
# %%
