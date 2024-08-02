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

    round_dt = npdatetime.round('15min')
    print(round_dt)
    return

    start_msg = int(dt[-4:])
    end_msg = start_msg + msg_res if (int(dt[-2:])+msg_res) < 60 else start_msg + (40+msg_res)
    start_data = int(f.split('_')[-4][1:])
    end_data = int(f.split('_')[-3][1:])
    if start_msg < start_data and start_data < end_msg \
        or start_msg < end_data and end_data < end_msg:
        closest_files.append(f)

def add_hail_class_to_netcdf(mwcch_file):
    
    with xr.open_dataset(mwcch_file) as ds:
        mwcch_data = ds.load()
    mwcch_data['hail_class'] = ('index', mwcch_read.get_hail_class(mwcch_data.POH.values))
    mwcch_data.to_netcdf(mwcch_file)

def get_MSG_timeseries(msg_path, last_timestamp, n_frames):
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

def crop_extent_over_location(msg_lon, msg_lat, loc_lon, loc_lat, cropsize):
    
    # find center of crop
    idx_lon_c = get_closest_index(msg_lon, loc_lon)
    idx_lat_c = get_closest_index(msg_lat, loc_lat)

    # shift center position away from edge to fit crop into domain
    idx_lon_c= add_padding_at_data_edge(idx_lon_c, len(msg_lon), cropsize/2.)
    idx_lat_c = add_padding_at_data_edge(idx_lat_c, len(msg_lat), cropsize/2.)

    # get indices of edges of crop
    idx_lon_min = idx_lon_c - int(cropsize/2.)
    idx_lon_max = idx_lon_min + int(cropsize)
    idx_lat_min = idx_lat_c - int(cropsize/2.)
    idx_lat_max = idx_lat_min + int(cropsize)

    # get corresponding lon lat extent
    lon_min = msg_lon[idx_lon_min]
    lon_max = msg_lon[idx_lon_max]
    lat_min = msg_lat[idx_lat_min]
    lat_max = msg_lat[idx_lat_max]

    return lon_min, lon_max, lat_min, lat_max

def crop_over_hail_area():
    return


# %%
# mwcch_path = "/net/merisi/pbigalke/data/MWCC-H/netcdf"
msg_path = "/data/sat/msg/netcdf/parallax"
mwcch_path = "/data/sat/products/PMW_sats/MWCCH_hail_probability/netcdf"

output_path = "/net/merisi/pbigalke/plots/data_investigation/constructing_dataset/casestudy_20220605"
if not os.path.exists(output_path):
    os.makedirs(output_path)

years = [2022]
months = [6]
days = [5]
msg_res = 15

# %%
n_frames = 8
cropsize = 128
channels = {'WV_062-IR_108': {"vmin":-60, "vmax":5}, 
            #'IR_108': {"vmin":200, "vmax":280}, 
  }  # 

# ---------------------------------------------------------------------
# load all mwcc-h files in study period
mwcch_files = match.get_files_in_study_period(mwcch_path, years, months=months, days=days)
print(len(mwcch_files))


# loop over mwcch files
for f in mwcch_files:
    print(f)

    # ---------------------------------------------------------------------
    # read in mwcc_file
    mwcch_data = mwcch_read.read(f)

    max_hail_class = mwcch_read.get_hail_class(np.max(mwcch_data.POH.values))
    print("max hail class, ", max_hail_class)
    if max_hail_class == "no_hail":
        print("no hail in this scene, implement random cropping here")
        # nur über overpass area ausschneiden sonst verfälscht
        continue
        
    # ---------------------------------------------------------------------
    # read in MSG time series ending in mwcc-h timestamp

    # get end time of overpass
    mwcch_end = mwcch_data.datetime.values[-1]

    # get corresponding MSG time series
    msg_data = get_MSG_timeseries(msg_path, mwcch_end, n_frames=n_frames)

        
    # ---------------------------------------------------------------------
    # find center of maximum hail area from mwcc-h data

    # mask mwcc-h data where maximum hail class occurs
    masked_data = mwcch_data.where(mwcch_data.hail_class == max_hail_class)

    # center of mass of maximum hail area
    cg_lat = np.sum(masked_data.lat * masked_data.POH)/np.sum(masked_data.POH)
    cg_lon = np.sum(masked_data.lon * masked_data.POH)/np.sum(masked_data.POH)
    
    # get extent of crop over hail area
    minlon, maxlon, minlat, maxlat = crop_extent_over_location(msg_data.lon.values, 
                                                                msg_data.lat.values, 
                                                                cg_lon, cg_lat, cropsize)

    # ---------------------------------------------------------------------
    # find center of OT proxy area (positive difference between WV_6.2 and IR_108)
    
    # find center of mass for area of highest convection in last frame
    ot_mask = msg_data.WV_062.isel(time=-1) - msg_data.IR_108.isel(time=-1) > 0
    masked_by_ot = msg_data.isel(time=-1).where(ot_mask)
    ot_proxy = masked_by_ot.WV_062 - masked_by_ot.IR_108
    ot_lon = np.sum(ot_proxy.lon * ot_proxy)/np.sum(ot_proxy)
    ot_lat = np.sum(ot_proxy.lat * ot_proxy)/np.sum(ot_proxy)

    # get extent of crop over OT area
    minlon_ot, maxlon_ot, minlat_ot, maxlat_ot = crop_extent_over_location(msg_data.lon.values,
                                                                            msg_data.lat.values, 
                                                                            ot_lon, ot_lat, cropsize)
    
    # ---------------------------------------------------------------------
    # loop over channels
    for channel in channels:

        # get data from channel
        if "-" in channel:
            chan1 = channel.split("-")[0]
            chan2 = channel.split("-")[1]
            print(chan1, chan2)
            msg_tb = msg_data[chan1] - msg_data[chan2]
        else:
            msg_tb = msg_data[channel]

        # ---------------------------------------------------------------------
        # plot for all timestamps in time series
        for t, ts in enumerate(msg_data.time.values[::-1]):
            if t == 0:
                # plot last timestamp with hail area crop
                dt = hlp.get_datetimestring_from_npdatetime(ts)
                title = f'{dt[:4]}-{dt[4:6]}-{dt[6:8]} {dt[-4:-2]}:{dt[-2:]}'
                outname = f"{output_path}/crop_over_maxhailarea/{dt}_{channel}_crop_over_maxhailarea.png"

                # plot crops over MSG and MWCC-H
                mwcc_plt.plot_mwcch_over_MSG(msg_data.lon.values, msg_data.lat.values, msg_tb.sel(time=ts), channel, 
                                            mwcch_data.lon.values, mwcch_data.lat.values, mwcch_data.POH.values, 
                                            mark_points=[[cg_lon, cg_lat, 'purple', 'x']], 
                                            draw_subdomains=[[minlon, maxlon, minlat, maxlat, 'purple', '-']], 
                                            vmin=channels[channel]["vmin"], vmax=channels[channel]["vmax"], 
                                            title=title, path_out=outname)
                
                # plot last timestamp with hail area crop
                title = f'{dt[:4]}-{dt[4:6]}-{dt[6:8]} {dt[-4:-2]}:{dt[-2:]}'
                outname = f"{output_path}/crop_over_maxhailarea_and_OTarea/{dt}_{channel}_crop_over_maxhailarea_and_OTarea.png"

                # plot crops over MSG and MWCC-H
                mwcc_plt.plot_mwcch_over_MSG(msg_data.lon.values, msg_data.lat.values, msg_tb.sel(time=ts), channel, 
                                            mwcch_data.lon.values, mwcch_data.lat.values, mwcch_data.POH.values, 
                                            mark_points=[[cg_lon, cg_lat, 'purple', 'x'], [ot_lon, ot_lat, 'g', 'x']], 
                                            draw_subdomains=[[minlon, maxlon, minlat, maxlat, 'purple', '-'],
                                                            [minlon_ot, maxlon_ot, minlat_ot, maxlat_ot, 'g', '-']], 
                                            vmin=channels[channel]["vmin"], vmax=channels[channel]["vmax"], 
                                            title=title, path_out=outname)


            # dt = hlp.get_datetimestring_from_npdatetime(ts)
            # title = f'{dt[:4]}-{dt[4:6]}-{dt[6:8]} {dt[-4:-2]}:{dt[-2:]}'
            # outname = f"{output_path}/{dt}_{channel}_crop_over_maxhailarea.png"
            # mwcc_plt.plot_mwcch_over_MSG(msg_data.lon.values, msg_data.lat.values, msg_data[channel].sel(time=ts), channel, 
            #                             mwcch_data.lon.values, mwcch_data.lat.values, mwcch_data.POH.values, 
            #                             mark_points=[[cg_lon, cg_lat, 'r', 'x']], 
            #                             draw_subdomains=[[minlon, maxlon, minlat, maxlat, 'r', '-']], 
            #                             vmin=vmin, vmax=vmax, title=title, path_out=outname)

                            



# %%
