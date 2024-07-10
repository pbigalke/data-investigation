# %%
import numpy as np
import os
import xarray as xr
import sys
sys.path.append("..")
# import my own script
import readers.read_MWCC_H as mwcc

def save_mwcch_over_domain_as_netcdf(mwcch_file, domain, output_path):
    
    # read in data file
    data = mwcc.read_mwcch_file(mwcch_file, domain=domain)

    if len(data) > 0:
        print('-----------------------------------------------------')
        print(mwcch_file)
        detector = mwcch_file.split('/')[-2]
        year, month, day = mwcc.get_y_m_d_from_mwcch_filepath(mwcch_file)
        print(year, month, day)

        count += 1
        # get date string from filename
        date_string = f"{year:04}{month:02}{day:02}"

        # get starting and end time within our domain
        start_time = f"S{int(np.min(data["hour"])):02}{int(np.min(data["min"])):02}"
        end_time = f"E{int(np.max(data["hour"])):02}{int(np.max(data["min"])):02}"
        
        # define netcdf file name
        netcdf_path = f"{output_path}/{year:04}/{month:02}/{day:02}"
        if not os.path.exists(netcdf_path):
            os.makedirs(netcdf_path)
        netcdf_file = f"{netcdf_path}/{date_string}_{start_time}_{end_time}_{detector}.nc"

        # save as netcdf file
        data_xr = xr.Dataset.from_dataframe(data)
        data_xr.to_netcdf(netcdf_file)

# %%
def main():
    path = "/net/merisi/pbigalke/data/MWCC-H/MWCC-H"
    output_path = "/net/merisi/pbigalke/data/MWCC-H/netcdf"
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
        save_mwcch_over_domain_as_netcdf(f, domain, output_path)
        count += 1

    print(count)
# %%
if __name__ == "__main__":
    main()
