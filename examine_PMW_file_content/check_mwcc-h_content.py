# Tiny script to print the file content of the original MWCCH-H files.
# use conda env my_satpy_env

# %%
import numpy as np
import xarray as xr
import os
import glob


# %%
# test reading MWCC-H files
common_path = "/net/merisi/pbigalke/data/MWCC-H/2022/"
examples = {"ATMS-n20": "ATMS/atms_20220331-S2254-E0036_n20_022624.asc",
            "ATMS-npp": "ATMS/atms_20220725-S1039-E1220_npp_055658.asc",
            "GMI": "GMI/BT_GMI_proxy_20220331-S2359-E0131_gpm_045959.asc",
            "MHS-meto01": "MHS/amsub_20220720_1831_meto01_51047_183WSLH.asc",
            "MHS-meto03": "MHS/amsub_20220920_0959_meto03_20081_183WSLH.asc",
            "MHS-noaa19": "MHS/amsub_20220720_1850_noaa19_69316_183WSLH.asc",
            "SSMIS-f16": "SSMIS/ssmis_20220401-S0133-E0315_f16_095209.asc",
            "SSMIS-f17": "SSMIS/ssmis_20220729-S1400-E1542_f17_081187.asc"
}

for k in examples.keys():
    print('-----------------------------------------------------------')
    print('---------------------------- ', k, '-----------------------')
    print('-----------------------------------------------------------')
    print(os.path.join(common_path, examples[k]))
    data = np.loadtxt(os.path.join(common_path, examples[k])).astype(str)#, skiprows=6)
    print(data[0:3])

# %%
