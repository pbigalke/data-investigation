# %%
import numpy as np
import os
import glob
import xarray as xr
import sys
sys.path.append("..")
# import my own script
import readers.read_MWCC_H as mwcc
import helpers.helper_conversions as hlp
from config.domain_info import domain_expats

# %%
def save_mwcch_over_domain_as_netcdf(mwcch_file, domain, output_path):
    
    # read in data file
    data = mwcc.read_mwcch_file(mwcch_file, domain=domain)

    if len(data) > 0:
        # get start and end datetime
        start_dt, end_dt = data['datetime'].agg(['min', 'max'])

        # get detector from filename
        detector = mwcc.get_detector_from_mwcch_filepath(mwcch_file)

        # get satellite name from filename
        satellite = mwcc.get_satellite_from_mwcch_filepath(mwcch_file)

        # get date string from start datetime
        date_string = hlp.get_datestring_from_npdatetime(start_dt)

        # get starting and end time within our domain
        start_time = f"S{hlp.get_timestring_from_npdatetime(start_dt)}"
        end_time = f"E{hlp.get_timestring_from_npdatetime(end_dt)}"
        
        # define netcdf file name
        netcdf_path = f"{output_path}/{date_string[:4]}/{date_string[4:6]}/{date_string[6:]}"
        if not os.path.exists(netcdf_path):
            os.makedirs(netcdf_path)
        netcdf_file = f"{netcdf_path}/{date_string}_{start_time}_{end_time}_{detector}_{satellite}.nc"

        # save as netcdf file
        data_xr = xr.Dataset.from_dataframe(data)
        data_xr.to_netcdf(netcdf_file)
        return True
    return False

# %%
def main():
    path = "/net/merisi/pbigalke/data/MWCC-H/H2MED_data"
    output_path = "/net/merisi/pbigalke/data/MWCC-H/netcdf"
    # years = [2022]
    # months = [6]
    # days = [5]
    # detectors = ["ATMS", "MHS", "SSMIS", "GMI"]
    # all_files = mwcc.get_mwcch_files_in_study_period(path, detectors, years, months, days)
    # print(len(all_files))
    # count = 0

    # read all files in directory
    all_files = sorted(glob.glob(f"{path}/*/*/*.asc.gz"))

    count = 0
    count_in_domain = 0
    # loop over files
    for f, fl in enumerate(all_files[:1000]):

        # print status every few files
        if f % 1000 == 0:
            print(f"{count}/{len(all_files)}: {count_in_domain} files within domain", flush=True)

        if save_mwcch_over_domain_as_netcdf(fl, domain_expats, output_path):
            count_in_domain += 1

        count += 1
# %%
if __name__ == "__main__":
    main()

# %%
