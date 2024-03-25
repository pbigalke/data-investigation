# use conda env my_satpy_env

# %%
import numpy as np
import xarray as xr
import os
import glob


# %%
# test reading MWCC-H files
common_path = "/net/merisi/pbigalke/data/MWCC-H/2022/"
examples = {"ATMS": "ATMS/atms_20220331-S2254-E0036_n20_022624.asc",
            "GMI": "GMI/BT_GMI_proxy_20220331-S2359-E0131_gpm_045959.asc",
            "MHS": "MHS/amsub_20220920_0959_meto03_20081_183WSLH.asc",
            "SSMIS": "SSMIS/ssmis_20220401-S0133-E0315_f16_095209.asc"
}

for k in examples.keys():
    print('-----------------------------------------------------------')
    print('---------------------------- ', k, '-----------------------')
    print('-----------------------------------------------------------')
    print(os.path.join(common_path, examples[k]))
    data = np.loadtxt(os.path.join(common_path, examples[k])).astype(str)#, skiprows=6)
    print(data[0:3])

# %%
