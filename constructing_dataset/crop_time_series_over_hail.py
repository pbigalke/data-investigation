# %%
import numpy as np
import pandas as pd
import xarray as xr
from scipy import ndimage as ndi
import glob
import os
import sys
sys.path.append('..')
import readers.read_MSG as msg_read
import readers.read_processed_MWCC_H as mwcch_read
import matching_data.collect_matching_files as match
import helpers.datetime_helper as hlp
import plotting.plot_MWCC_H as mwcc_plt
from config.domain_info import domain_expats


# %%
def get_neighboring_datestring_from_npdatetime(npdatetime, which="both"):

    dt = hlp.get_datestring_from_npdatetime(npdatetime)

    if which == "previous":
        prev_dt = hlp.get_datestring_from_npdatetime(npdatetime - pd.DateOffset(days=1))
        return [prev_dt, dt]
    elif which == "following":
        foll_dt = hlp.get_datestring_from_npdatetime(npdatetime + pd.DateOffset(days=1))
        return [dt, foll_dt]
    else:
        prev_dt = hlp.get_datestring_from_npdatetime(npdatetime - pd.DateOffset(days=1))
        foll_dt = hlp.get_datestring_from_npdatetime(npdatetime + pd.DateOffset(days=1))
        return [prev_dt, dt, foll_dt]


def get_corresponding_msg_files(directory, timestamps):

    msg_files = []
    for ts in timestamps:
        dt = hlp.get_datestring_from_npdatetime(ts)
        msg_files.append(f"{directory}/{dt[:4]}/{dt[4:6]}/{dt[:8]}-EXPATS-RG.nc")
    return msg_files
    

def get_closest_msg_timestamp(npdatetime, msg_res=15):

    round_dt = npdatetime.round(f'{msg_res}min')
    print(round_dt)
    return

def add_hail_class_to_netcdf(mwcch_file):
    
    with xr.open_dataset(mwcch_file) as ds:
        mwcch_data = ds.load()
    mwcch_data['hail_class'] = ('index', mwcch_read.get_hail_class(mwcch_data.POH.values))
    mwcch_data.to_netcdf(mwcch_file)

def get_MSG_timeseries(msg_path, last_timestamp, msg_res, n_frames):
    # get closest MSG timestamp from overpass end time
    last_frame = pd.Timestamp(last_timestamp).round(f'{msg_res}min').to_datetime64()

    # create MSG time series of given length ending in overpass
    time_series = last_frame - pd.to_timedelta(np.arange(n_frames)[::-1]*msg_res, 'm')

    # find MSG daily files that this time series covers
    days_in_time_series = time_series.normalize().unique().values
    msg_files = get_corresponding_msg_files(msg_path, days_in_time_series)

    msg_time_series = []
    # loop over MSG files
    for msg in msg_files:

        # read MSG data
        msg_data = msg_read.read(msg)

        # select only timestamps that are covered by time series
        msg_time_series.append(msg_data.where(msg_data.time.isin(time_series), drop=True))
    
    #msg_time_series = xr.concat(msg_time_series, dim=['time'])
    # merge separate daily
    msg_time_series = xr.merge(msg_time_series)
    return msg_time_series

def get_center_of_mass_for_variable(lon, lat, variable):
    cg_lat = np.sum(lat * variable) / np.sum(variable)
    cg_lon = np.sum(lon * variable) / np.sum(variable)
    return cg_lon, cg_lat

def get_closest_index(arr, val):
    idx = np.searchsorted(arr, val)
    # clip to last index
    if idx == len(arr):
        idx = -1
    # find closest neighbors
    if (val - arr[idx-1]) <= (arr[idx] - val):
        idx -= 1
    return idx

def add_padding_at_data_edge(idx, data_dim, padding):
    # shift center point away from domain borders to fit whole crop
    if idx < padding:
        idx = int(padding)
    elif idx > (data_dim-1 - padding):
        idx = int(data_dim-1 - padding)
    return idx

def get_crop_extent_from_center_choords(msg_lon, msg_lat, loc_lon, loc_lat, cropsize):
    
    # find center of crop
    idx_lon_c = get_closest_index(msg_lon, loc_lon)
    idx_lat_c = get_closest_index(msg_lat, loc_lat)

    # shift center position away from edge to fit crop into domain
    idx_lon_c= add_padding_at_data_edge(idx_lon_c, len(msg_lon), cropsize/2.)
    idx_lat_c = add_padding_at_data_edge(idx_lat_c, len(msg_lat), cropsize/2.)

    # get indices of edges of crop
    idx_lon_min = idx_lon_c - int(cropsize/2.)
    idx_lon_max = idx_lon_min + int(cropsize) - 1
    # need to substract 1 as xr.dataset.sel(lon=slice(minlon, maxlon)) includes the edges
    idx_lat_min = idx_lat_c - int(cropsize/2.)
    idx_lat_max = idx_lat_min + int(cropsize) - 1

    # get corresponding lon lat extent
    lon_min = msg_lon[idx_lon_min]
    lon_max = msg_lon[idx_lon_max]
    lat_min = msg_lat[idx_lat_min]
    lat_max = msg_lat[idx_lat_max]

    return lon_min, lon_max, lat_min, lat_max

def get_crop_extent_over_maxhailarea(msg_timeseries, mwcch_data, cropsize):

    # get max hail class in mwcch data
    max_hail_class = mwcch_read.get_hail_class(np.max(mwcch_data.POH.values))

    # if no hail is present TODO: implement solution for this case
    if max_hail_class == "no_hail":
        print("no hail in this scene, implement random cropping here")
        # nur über overpass area ausschneiden sonst verfälscht
        return None
    
    # mask mwcc-h data where maximum hail class occurs
    masked_data = mwcch_data.where(mwcch_data.hail_class == max_hail_class)

    # calculate center of mass for variable
    cg_lon, cg_lat = get_center_of_mass_for_variable(masked_data.lon, masked_data.lat, masked_data.POH)
    
    # get extent of crop over hail area
    minlon, maxlon, minlat, maxlat = get_crop_extent_from_center_choords(msg_timeseries.lon.values, msg_timeseries.lat.values, 
                                                                         cg_lon, cg_lat, cropsize)
    return cg_lon.values, cg_lat.values, minlon, maxlon, minlat, maxlat

def recenter_crop_over_highest_clouds(msg_timeseries, crop_extent, mode="all"):

    # get difference between 6.2 and 10.8 channels
    diffWVIR = msg_timeseries.WV_062.isel(time=-1) - msg_timeseries.IR_108.isel(time=-1)

    # only lokk at values within original crop over hail area
    diffWVIR_in_crop = diffWVIR.sel(lon=slice(crop_extent[0], crop_extent[1]), lat=slice(crop_extent[2], crop_extent[3]))

    # get cropsize
    cropsize = len(diffWVIR_in_crop.lon.values)

    # if looking only at OT proxy
    if mode == "OT":
        # consider only positive difference values (=OT)
        diffWVIR_in_crop = diffWVIR_in_crop.where(diffWVIR > 0)

    # find center of mass for diff-WV-IR values WITHIN FIRST CROP OVER HAIL AREA
    cg_lon_recentered = np.sum(diffWVIR_in_crop.lon * diffWVIR_in_crop) / np.sum(diffWVIR_in_crop)
    cg_lat_recentered = np.sum(diffWVIR_in_crop.lat * diffWVIR_in_crop) / np.sum(diffWVIR_in_crop)

    # overwrite hail area crop with new recentered crop extent
    minlon, maxlon, minlat, maxlat = get_crop_extent_from_center_choords(msg_timeseries.lon.values, msg_timeseries.lat.values, 
                                                                            cg_lon_recentered, cg_lat_recentered, cropsize)
    
    return cg_lon_recentered.values, cg_lat_recentered.values, minlon, maxlon, minlat, maxlat

def add_attributes(msg_timeseries, cg_lon, cg_lat, cg_lon_recentered=None, cg_lat_recentered=None):
    # add global attributes about the data
    description = "MSG time series cropped over location of hail area in last frame " + \
        "detected by the PMW satellite hail probability MWCC-H."
    start_time = hlp.get_datetimestring_from_npdatetime(msg_timeseries.time.values[0])
    end_time = hlp.get_datetimestring_from_npdatetime(msg_timeseries.time.values[-1])
    n_frames = len(msg_timeseries.time.values)
    n_pixel = len(msg_timeseries.lon.values)
    hail_area_lon = cg_lon
    hail_area_lat = cg_lat
    recentered_lon = "" if cg_lon_recentered is None else cg_lon_recentered
    recentered_lat = "" if cg_lat_recentered is None else cg_lat_recentered

    msg_timeseries = msg_timeseries.assign_attrs(description=description, 
                                                 start_time=start_time, end_time=end_time, 
                                                 n_frames=n_frames, n_pixel=n_pixel, 
                                                 hail_area_lon=hail_area_lon, hail_area_lat=hail_area_lat, 
                                                 recentered_lon=recentered_lon, recentered_lat=recentered_lat)
    return msg_timeseries
    
def crop_and_save_MSG_timeseries(msg_timeseries, mwcch_data, cropsize, filepath, recenter=None):

    # get extent of crop over max hail class area
    cg_lon, cg_lat, minlon, maxlon, minlat, maxlat = \
        get_crop_extent_over_maxhailarea(msg_timeseries, mwcch_data, cropsize)
    
    if recenter is not None:
        # recenter crop over highest cloud area within crop
        cg_lon_recentered, cg_lat_recentered, minlon, maxlon, minlat, maxlat = \
            recenter_crop_over_highest_clouds(msg_timeseries, [minlon, maxlon, minlat, maxlat], mode=recenter)

    # return cropped dataset
    msg_timeseries = msg_timeseries.sel(lon=slice(minlon, maxlon), lat=slice(minlat, maxlat))
    
    # add global attributes describing the data
    msg_timeseries = add_attributes(msg_timeseries, cg_lon, cg_lat, 
                                    cg_lon_recentered=None if recenter is None else cg_lon_recentered, 
                                    cg_lat_recentered=None if recenter is None else cg_lat_recentered)

    # save to given filepath
    msg_timeseries.to_netcdf(filepath)



# %%
def construct_MSG_timeseries(recenter=None):
    # mwcch_path = "/net/merisi/pbigalke/data/MWCC-H/netcdf"
    msg_path = msg_read.MSG_PATH
    mwcch_path = mwcch_read.MWCCH_PATH
    
    recenter_suffix = "" if recenter is None else f"_recentered_{recenter}"
    output_path = f"/net/merisi/pbigalke/data/MSG_timeseries_maxhailarea{recenter_suffix}"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # study period settings
    years = [2022]
    months = [6]
    days = [5]

    # time series settings
    msg_res = 15
    n_frames = 8
    cropsize = 128

    # ---------------------------------------------------------------------
    # load all mwcc-h files in study period
    mwcch_files = match.get_files_in_study_period(mwcch_path, years, months=months, days=days)

    # loop over mwcch files
    for f in mwcch_files:
        print(f, flush=True)

        # ------------------------------------------------------------ read MWCC-H
        # read in mwcc_file
        mwcch_data = mwcch_read.read(f)

        # ------------------------------------------------------------ get label
        # set label to maximum hail class within domain
        label = mwcch_read.get_hail_class(np.max(mwcch_data.POH.values))
        print(label, flush=True)
        if label == "no_hail":
            continue

        # define output path for this label
        path_label = os.path.join(output_path, label)
        if not os.path.exists(path_label):
            os.makedirs(path_label)
           
        # ------------------------------------------------------------ create MSG time serie
        # read in MSG time series ending in mwcc-h timestamp

        # get end time of overpass
        mwcch_end = mwcch_data.datetime.values[-1]

        # get corresponding MSG time series
        msg_timeseries = get_MSG_timeseries(msg_path, mwcch_end, msg_res, n_frames)

        # add global attribute about 

        # define output filename
        dt_end = hlp.get_datetimestring_from_npdatetime(msg_timeseries.time.values[-1])
        filepath = os.path.join(path_label, f"{dt_end}_{n_frames}frames_{cropsize}pix{recenter_suffix}.nc")

        # crop and save timeseries over hail event
        crop_and_save_MSG_timeseries(msg_timeseries, mwcch_data, cropsize, filepath, recenter=recenter)
        
   

# %%
if __name__ == "__main__":
    construct_MSG_timeseries()
    # no hail
    # 20220605_S0340_E0341_SSMIS_f16.nc
    # 20220605_S1017_E1017_MHS_meto03.nc    
    # 20220605_S1820_E1821_SSMIS_f17.nc

# %%
