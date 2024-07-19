
# %%
import xarray as xr
import sys
sys.path.append("..")
import matching_data.collect_matching_files as clct

# %%
def read(file_path):
    """ read processed MWCC-H output containing probability of hail
    """
    with xr.open_dataset(file_path) as dataset:
        return dataset

def get_y_m_d_from_filepath(file_path):
    
    return None


# %%
if __name__ == '__main__':
    import numpy as np
    # test on exaple file
    example_file = "mhs_METOPB_20230724-S1905-E2046_056289"
    satellite = 'METOPB'
    
    path = "/net/merisi/pbigalke/data/MWCC-H/netcdf"
    years = [2022]
    months = [6]
    days = [5]
    detectors = ["ATMS", "MHS", "SSMIS"]
    all_files = clct.get_mwcch_files_in_study_period(path, detectors, years, months, days)
    for f in all_files:
        print(f)

# %%
