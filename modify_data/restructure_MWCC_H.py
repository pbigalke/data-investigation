# %%
import numpy as np
import os
import xarray as xr
import sys
sys.path.append("..")
# import my own script
import readers.read_MWCC_H as mwcc

# %%
path = "/net/merisi/pbigalke/data/MWCC-H"
years = [2022]
months = [6]
days = [5]
detectors = ["ATMS", "MHS", "SSMIS"]
all_files = mwcc.get_mwcch_files_in_study_period(path, detectors, years, months, days)

print(len(all_files))
count = 0

# define domain
domain = {"minlon":5., "maxlon":16., "minlat":42., "maxlat":51.5}
for f in all_files:

    # read in data file
    data = mwcc.read_mwcch_file(f, domain=domain)

    if len(data) > 0:
        print('-----------------------------------------------------')
        print(f)
        base_path = "/".join(f.split('/')[:-3] + ["netcdf"])
        detector = f.split('/')[-2]
        year, month, day = mwcc.get_y_m_d_from_mwcch_filepath(f)
        print(year, month, day)

        count += 1
        # get date string from filename
        date_string = f"{year:04}{month:02}{day:02}"

        # get starting and end time within our domain
        start_time = f"S{int(np.min(data["hour"])):02}{int(np.min(data["min"])):02}"
        end_time = f"E{int(np.max(data["hour"])):02}{int(np.max(data["min"])):02}"
        
        # define netcdf file name
        file_path = f"{base_path}/{year:04}/{month:02}/{day:02}"
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        file_name = f"{file_path}/{date_string}_{start_time}_{end_time}_{detector}.nc"
        print(file_name)
        data_xr = xr.Dataset.from_dataframe(data)
        data_xr.to_netcdf(file_name)

print(count)
# %%
