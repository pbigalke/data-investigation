
# %%
import xarray as xr
import numpy as np
import sys
sys.path.append("..")
import matching_data.collect_matching_files as clct

# %%
def read(file_path):
    """ read processed MWCC-H output containing probability of hail
    """
    return xr.open_dataset(file_path)

def get_y_m_d_from_filepath(file_path):
    
    return None

def get_sat_from_filepath(file_path):
    satellites = ['meto01', 'meto02', 'meto03', 'noaa15', 'noaa16', 'noaa17', 'noaa18', 'noaa19', 
                  'n20', 'n21', 'npp', 'f16', 'f17', 'gpm']
    for sat in satellites:
        if sat in file_path.lower():
            return sat
    return None

def get_hail_class(poh):
    hail_classes = ["no_hail", 
                    "hail_potential", 
                    "hail_initiation_graupel", 
                    "large_hail", 
                    "super_hail"]
    boundaries = [0, 0.2, 0.36, 0.45, 0.6, 1.01]
    idx = np.searchsorted(boundaries, poh, side='right') - 1
    return np.take(hail_classes, idx)

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
