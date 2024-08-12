
# %%
import xarray as xr
import numpy as np
import os
import sys
sys.path.append("..")
import matching_data.collect_matching_files as clct

MWCCH_PATH = "/data/sat/products/PMW_sats/MWCCH_hail_probability/netcdf"

# %%
def read(file_path):
    """ read processed MWCC-H output containing probability of hail
    """
    with xr.open_dataset(file_path, engine="netcdf4") as dataset:
        return dataset

def get_y_m_d_from_filepath(file_path):
    print("not implemented yet")
    return None

def get_start_and_end_datetimes_from_filepath(file_path):
    split_file = os.path.basename(file_path).split('_')
    date = split_file[0]
    starttime = split_file[1][1:]
    endtime = split_file[2][1:]
    start_datetime = np.datetime64(f'{date[:4]}-{date[4:6]}-{date[6:]}T{starttime[:2]}:{starttime[2:]}')
    end_datetime = np.datetime64(f'{date[:4]}-{date[4:6]}-{date[6:]}T{endtime[:2]}:{endtime[2:]}')
    return start_datetime, end_datetime

def get_sat_from_filepath(file_path):
    satellites = ['meto01', 'meto02', 'meto03', 'noaa15', 'noaa16', 'noaa17', 'noaa18', 'noaa19', 
                  'n20', 'n21', 'npp', 'f16', 'f17', 'gpm']
    for sat in satellites:
        if sat in file_path.lower():
            return sat
    return None

def get_hail_class(poh=None, type="number"):
    # define hail classes, the entry np.NaN is assigned to poh=NaN
    if type == "name":
        hail_classes = ["no_hail", 
                        "hail_potential", 
                        "hail_initiation_graupel", 
                        "large_hail", 
                        "super_hail", 
                        np.NaN]
    else:
        hail_classes = [0, 1, 2, 3, 4, np.NaN]

    if poh is None:
        return hail_classes[:-1]
    
    # if only one values is given
    if isinstance(poh, float):
        poh = np.array(poh)

    # define boundaries of hail classes
    boundaries = [0, 0.2, 0.36, 0.45, 0.6, 1.01]

    # search for hail class corresponding to given poh
    idx = np.searchsorted(boundaries, poh.ravel(), side='right') - 1
    hail_classes = np.take(hail_classes, idx)

    # reshape into original shape
    hail_classes = hail_classes.reshape(poh.shape)

    return hail_classes

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
