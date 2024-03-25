# use conda env my_satpy_env

# %%
import numpy as np
import xarray as xr
import os
import glob


# %%
# test reading MWCC-H files
path_mwcch = "net/merisi/pbigalke/data/MWCC-H/2019/"
detectors = ["ATMS", "GMI", "MHS", "SSMIS"]

for det in detectors:
    print('------------ detector: ', det)
    path_detector = os.path.join(path_mwcch, det)

    files = glob.glob(path_detector)
    print(files)

# %%
