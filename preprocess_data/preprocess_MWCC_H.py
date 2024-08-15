# %%
import os
import glob
import xarray as xr
import pandas as pd
import scipy
from scipy.interpolate import griddata
import numpy as np
import sys
sys.path.append("..")
# import my own script
import matching_data.collect_matching_files as match
import readers.read_processed_MWCC_H as mwcch
import readers.read_MSG as msg
import plotting.plot_MWCC_H as mwcch_plt
from config.domain_info import domain_expats

mwcch_path_raw = "/data/sat/products/PMW_sats/MWCCH_hail_probability/MWCC-H_raw"
mwcch_path_netcdf = "/data/sat/products/PMW_sats/MWCCH_hail_probability/netcdf"
mwcch_path_netcdf_msggrid = "/data/sat/products/PMW_sats/MWCCH_hail_probability/netcdf_MSG_grid"

# %%
def save_all_MWCCH_data_as_netcdf():
    path = mwcch_path_raw
    output_path = mwcch_path_netcdf
    years = [2022]
    months = [6]
    days = [5]
    detectors = ["ATMS", "MHS", "SSMIS", "GMI"]
    all_files = match.get_mwcch_files_in_study_period(path, detectors, years, months, days)
    print(len(all_files))

    # read all files in directory
    # all_files = sorted(glob.glob(f"{path}/*/*/*.asc.gz"))

    count = 0
    count_in_domain = 0
    # loop over files
    for f, fl in enumerate(all_files):

        # print status every few files
        if f % 1000 == 0:
            print(f"{count}/{len(all_files)}: {count_in_domain} files within domain", flush=True)

        if save_mwcch_over_domain_as_netcdf(fl, domain_expats, output_path):
            count_in_domain += 1

        count += 1

def add_hail_class_to_netcdf():
    output_path = mwcch_path_netcdf

    # read all files in directory
    # all_files = sorted(glob.glob(f"{output_path}/*/*/*/*.nc"))
    # print(len(all_files), flush=True)

    years = [2022]
    months = [6]
    days = [5]
    all_files = match.get_files_in_study_period(output_path, years, months, days)
    print(len(all_files))

    count = 0
    # loop over files
    for f, fl in enumerate(all_files):

        # print status every few files
        if f % 1000 == 0:
            print(f"{count}/{len(all_files)}", flush=True)

        # add hail class to all data files
        add_hail_class_to_netcdf(fl)

        count += 1

def regrid_all_MWCCH_data_to_MSG_grid(overwrite=False):

    original_path = mwcch_path_netcdf
    #all_files = sorted(glob.glob(f"{original_path}/*/*/*/*.nc"))
    output_path = mwcch_path_netcdf_msggrid

    years = np.arange(1999, 2024, 1) #[2022]
    months = np.arange(4, 10, 1) #[6]
    days = np.arange(1, 32, 1) #[5]
    # years = [2022]
    # months = [6]
    # days = [5]

    # get MSG lon and lat
    msg_lon, msg_lat = msg.get_lon_lat()

    print(f"overwrite = {overwrite}.", flush=True)
    if overwrite:
        count = 0
        print("all files will be overwritten.", flush=True)
    else:
        count = len(glob.glob(f"{output_path}/*/*/*/*.nc"))
        print(f"{count} files will not be overwritten.", flush=True)

    for year in years:
        for month in months:
            for day in days:
                files_day = match.get_files_in_study_period(original_path, year, month, day)
                
                # loop over files
                for fl in files_day:

                    # generate new filename
                    start_dt, end_dt = mwcch.get_start_and_end_datetimes_from_mwcch_filepath(fl)
                    regrid_file = mwcch.generate_mwcch_filepath(output_path, start_dt, end_dt, 
                                                                mwcch.get_detector_from_mwcch_filepath(fl), 
                                                                mwcch.get_sat_from_mwcch_filepath(fl),
                                                                suffix="_MSGgrid")
                    # if not overwrite continue if file exists
                    if not overwrite and os.path.exists(regrid_file):
                        continue
        
                    # regrid and save to new file
                    regrid_and_save_file(fl, msg_lon, msg_lat, regrid_file)
                    count += 1

                    # print status every few files
                    if count % 1000 == 0:
                        print(f"{count}", flush=True)

    print("total number of files: ", count, flush=True)

def regrid_and_save_file(mwcch_file, msg_lon, msg_lat, output_file):
    # read hail data
    data = mwcch.read(mwcch_file)
    vars = [k for k in data.keys() if k not in ['lon', 'lat', 'hail_class']]

    # continue if enough data points are within domain, 4 is threshold for regridding method
    if len(data.POH.values) >= 4:

        # create new dataset with MSG lon and lat grid
        mwcch_regrid = xr.Dataset(coords=dict(lat=("lat", msg_lat),
                                                lon=("lon", msg_lon)))
        # add start and end datetime
        start_dt, end_dt = mwcch.get_start_and_end_datetimes_from_mwcch_filepath(mwcch_file)
        mwcch_regrid.attrs['start_scan'] =  np.datetime_as_string(start_dt, unit='m')
        mwcch_regrid.attrs['end_scan'] = np.datetime_as_string(end_dt, unit='m')
        # add information on satellite and detector
        mwcch_regrid.attrs['satellite'] = mwcch.get_sat_from_mwcch_filepath(mwcch_file)
        mwcch_regrid.attrs['detector'] = mwcch.get_detector_from_mwcch_filepath(mwcch_file)

        # loop over variables, to regrid and save to new dataset
        for var in vars:

            try:
                # regrid to MSG grid
                var_regrid = regrid_file_to_MSG(data.lon.values, data.lat.values, 
                                                data[var].values, msg_lon, msg_lat)
                # add to new dataset
                mwcch_regrid[var] = (['lat', 'lon'], var_regrid)
            except scipy.spatial._qhull.QhullError:
                print("error in input data:", mwcch_file, flush=True)
                print("data lon", data.lon.values.shape, data.lon, flush=True)
                print("data lat", data.lat.values.shape, data.lat, flush=True)
                print("data values", data[var].values.shape, data[var], flush=True)
                return
        
        # add hail class
        hail_class_arr = mwcch.get_hail_class(poh=mwcch_regrid["POH"].values, type="number")
        hail_classes = mwcch.get_hail_class(poh=None, type="number")
        hail_classes_names = mwcch.get_hail_class(poh=None, type="name")
        description = "hail classes are defined as follows: "
        for h in hail_classes:
            description += f"\n{h}: {hail_classes_names[h]}"
        mwcch_regrid["hail_class"] = (['lat', 'lon'], hail_class_arr, {"description": description})

        # save as netcdf file
        mwcch_regrid.to_netcdf(output_file)
    return

def regrid_file_to_MSG(points_lon, points_lat, points_values, msg_lon, msg_lat, method='linear'):
    """regrid data points to MSG regular grid
    Args:
        points_lon (1Darray(float)): longitude positions of data points
        points_lat (1Darray(float)): latitude positions of data points
        points_values (1Darray(float)): values of data points
        msg_lon (1Darray(float)): longitudes of of regular MSG grid, 1D-array
        msg_lat (1Darray(float)): latitudes of of regular MSG grid, 1D-array
        method (str, optional): Method for interpolation as used in scipy.griddata(). Defaults to 'linear'.
    Returns:
        regridded data (2Darray(float)): data regridded to regular MSG grid
    """
    # join coordinates of point data
    old_coords = (points_lon, points_lat)

    # Create a mesh of MSG grid coordinates
    lons, lats = np.meshgrid(msg_lon, msg_lat)
    
    # join coordinates of all points in MSG grid
    new_coords = (lons, lats)

    # Interpolate old data to new grid using the specified method
    new_data = griddata(old_coords, points_values, new_coords, method=method)


    return new_data 

def test_regridding_on_example():
    example = f"{mwcch_path_netcdf}/2022/06/05/20220605_S0518_E0522_SSMIS_f16.nc"
    data = mwcch.read(example)

    # get MSG lon and lat
    msg_lon, msg_lat = msg.get_lon_lat()

    # regrid data to MSG
    regrid = regrid_file_to_MSG(data.lon.values, data.lat.values, data.POH.values, 
                                msg_lon, msg_lat, method='linear')

    for mode in ['poh', 'hail_class']:
        # plot data
        mwcch_plt.plot_mwcch_over_map(data.lon.values, data.lat.values, data.POH.values, mwcch_mode=mode)
        # plot regridded data
        mwcch_plt.plot_mwcch_over_map(msg_lon, msg_lat, regrid, mwcch_mode=mode)

def add_hail_class_to_netcdf(mwcch_file):
    
    with xr.open_dataset(mwcch_file) as ds:
        
        if "hail_class" in list(ds.keys()):
            return
        
        mwcch_data = ds.load()

    mwcch_data['hail_class'] = ('index', mwcch.get_hail_class(mwcch_data.POH.values))
    mwcch_data.to_netcdf(mwcch_file)
    return

# %%
def save_mwcch_over_domain_as_netcdf(mwcch_file, domain, output_path=None):
    
    # read in data file
    data = _read_raw_mwcch_file(mwcch_file, domain=domain)

    if len(data) > 0:
        # get start and end datetime
        start_dt, end_dt = data['datetime'].agg(['min', 'max'])

        # get detector from filename
        detector = mwcch.get_detector_from_mwcch_filepath(mwcch_file)

        # get satellite name from filename
        satellite = mwcch.get_sat_from_mwcch_filepath(mwcch_file)
        
        if output_path is not None:

            netcdf_file = mwcch.generate_mwcch_filepath(output_path, start_dt, end_dt, detector, satellite)

            # save as netcdf file
            data_xr = xr.Dataset.from_dataframe(data)
            data_xr.to_netcdf(netcdf_file)
            print(f"saved to {netcdf_file}")
        return True
    return False

def _crop_over_domain(data, domain):
    """ crops data over given domain

    Parameters
    ----------
    data : pandas dataframe
        MWCC-H output after conversion into dataframe
    domain : dict
        containing "minlon", "maxlon", "minlat", "maxlat"

    Returns
    -------
    pandas dataframe
        MWCC-H output cropped over domain
    """
    # select only our domain
    mask_out_of_bounds = (data.lon < domain[0]) | (data.lon > domain[1]) | \
                (data.lat < domain[2]) | (data.lat > domain[3])
    index_out_of_bounds = data[mask_out_of_bounds].index
    data.drop(index_out_of_bounds, inplace=True)
    return data

def _read_raw_mwcch_file(file_path, domain=None):
    """ read MWCC-H output containing probability of hail into dataframe

    Parameters
    ----------
    filename : string or path
        path to file
    domain : dict, optional
        if not None data is cropped to this domain,
        containing "minlon", "maxlon", "minlat", "maxlat", by default None

    Returns
    -------
    pandas dataframe
        MWCC-H output (cropped) as dataframe with column names
    """
    # read file
    df_raw = pd.read_csv(file_path, sep='\t', header=None)

    # rearrange the data into proper dataframe
    df = df_raw[0].str.split(expand=True).astype(float)
    
    # add the names of columns
    df.columns = ['year', 'month', 'day', 'hour', 'minute', 'second', 'lat', 'lon', 'cloud_type', 'TB', 'POH']

    if domain is not None:
        # select only over given domain
        df = _crop_over_domain(df, domain)

    # add another column containing datetime
    df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour', 'minute', 'second']])

    # sort new and leave out unnecessary date and time columns
    df = df[ ['datetime'] + ['lat'] + ['lon'] + ['cloud_type'] + ['TB'] + ['POH'] ]
    
    return df
# %%
# def _get_column_names(detector):
#     """ read column names depending on satellite

#     Parameters
#     ----------
#     detector : string
#         detector that was used

#     Returns
#     -------
#     list(string)
#         names of columns in data file - differs for different satellites!! TODO: add other satellites here!
#     """
#     if detector == "ATMS":
#         return ['scan', 'fov', 'year', 'month', 'day', 'hour', 'min', 'sec', 'lat', 'lon', 'cloud_type', 'tb_165', 'POH']
    
#     elif detector == "GMI":
#         return ['scan', 'fov', 'lat', 'lon', 'tb_89h', 'tb_166v', 'tb_166h', 'tb_186v', 'tb_186h', 'POH']
    
#     elif detector == "MHS":
#         return ['scan', 'fov', 'year', 'month', 'day', 'hour', 'min', 'sec', 'lat', 'lon', 'rr', 'flag1', 'flag2', 'flag3', 'flag4', 'POH']
    
#     elif detector == "SSMIS":
#         return ['year', 'month', 'day', 'hour', 'min', 'sec', 'lat', 'lon', 'cloud_type', 'tb_150', 'POH']

# def _read_mwcch_file_old(file_path, domain=None):
#     """ read MWCC-H output containing probability of hail into dataframe

#     Parameters
#     ----------
#     filename : string or path
#         path to file
#     domain : dict, optional
#         if not None data is cropped to this domain,
#         containing "minlon", "maxlon", "minlat", "maxlat", by default None

#     Returns
#     -------
#     pandas dataframe
#         MWCC-H output (cropped) as dataframe with column names
#     """
#     # read detector name from file_path
#     detector = file_path.split('/')[-2]
    
#     # read file
#     df_raw = pd.read_csv(file_path, sep='\t', header=None)

#     # rearrange the data into proper dataframe
#     df = df_raw[0].str.split(expand=True).astype(float)

#     # add the names of columns
#     df.columns = _get_column_names()

#     if domain is not None:
#         # select only over given domain
#         df = _crop_over_domain(df, domain)

#     # add another column containing datetime
#     #df.insert(loc = 0,
#     #         column = 'datetime',
#     #         value =  df.apply(lambda x : datetime(int(x['year']), int(x['month']), int(x['day']), int(x['hour']), int(x['min']), int(x['sec'])), axis=1))
#     return df




# %%
if __name__ == "__main__":
    # main()
    # main_add_hail_class()

    # regrid_all_MWCCH_data_to_MSG_grid(overwrite=True)
    test_regridding_on_example()

    # path = "/net/merisi/pbigalke/data/MWCC-H/H2MED_data"
    # outpath = "/net/merisi/pbigalke/data/MWCC-H/netcdf"
    # years = [2022]
    # months = [6]
    # days = [5]
    # detectors = ["ATMS", "MHS", "SSMIS", "GMI"]
    # all_files = _get_mwcch_files_in_study_period(path, detectors, years, months, days)
    # for f in all_files:
    #     if save_mwcch_over_domain_as_netcdf(f, domain_expats, output_path=outpath):
    #         print(os.path.basename(f))

# %%
