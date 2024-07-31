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
# mwcch_path = "/net/merisi/pbigalke/data/MWCC-H/netcdf"
msg_path = "/data/sat/msg/netcdf/parallax"
mwcch_path = "/data/sat/products/PMW_sats/MWCCH_hail_probability/netcdf"

output_path = "/net/merisi/pbigalke/plots/data_investigation/constructing_dataset"
if not os.path.exists(output_path):
    os.makedirs(output_path)

years = [2022]
months = [6]
days = [5]
msg_res = 15

mwcch_files = match.get_files_in_study_period(mwcch_path, years, months=months, days=days)
print(len(mwcch_files))

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
    
    mwcch_data = mwcch_read.read(mwcch_file)
    mwcch_data['hail_class'] = ('index', mwcch_read.get_hail_class(mwcch_data.POH.values))
    # mwcch_data.drop_encoding()
    mwcch_data.to_netcdf(mwcch_file)

# %%
n_frames = 12

for f in mwcch_files:
    print()
    # print(os.path.basename(f))

    # read in mwcc_file
    mwcch_data = mwcch_read.read(f)
    print(mwcch_data)
    #add_hail_class_to_netcdf(f)

    break

    # get end time of overpass
    mwcch_end = mwcch_data.datetime.values[-1]
    hail_classes = get_hail_class(mwcch_data.POH.values)

    mwcch_data['hail_class'] = ('index', hail_classes)
    print(hail_classes)
    break


    # find area of highest hail
    # # calculate center of mass of max frequency area
    # com = ndi.measurements.center_of_mass(mwcch_data.POH)

    # if np.isnan(com[0]) or np.isnan(com[1]): 
    #         continue  
    # idx_lon = int(np.round(com[0]))
    # idx_lat = int(np.round(com[1]))
    # lon_center = lons_1d[idx_lon]
    # lat_center = lats_1d[idx_lat]


    
    # center of mass in y
    cg_lat = np.sum(mwcch_data.lat * mwcch_data.POH)/np.sum(mwcch_data.POH)
    cg_lon = np.sum(mwcch_data.lon * mwcch_data.POH)/np.sum(mwcch_data.POH)
    print(cg_lat, cg_lon)

    pohmax_lat = np.argwhere()

    mwcc_plt.plot_mwcch_over_map(mwcch_data.lon.values, mwcch_data.lat.values, mwcch_data.POH.values, domain=domain_expats, 
                                 mark_points=[[cg_lon],[cg_lat]])
    break

# def crop_MSG_timeseries(msg_path, last_timestamp, n_frames, domain):
    # get closest MSG timestamp from overpass end time
    last_frame = pd.Timestamp(mwcch_end).round(f'{msg_res}min').to_datetime64()

    # create MSG time series of given length ending in overpass
    time_series = last_frame - pd.to_timedelta(np.arange(n_frames)[::-1]*msg_res, 'm')

    # find MSG daily files that this time series covers
    days_in_time_series = time_series.normalize().unique().values
    msg_files = get_corresponding_msg_files(msg_path, days_in_time_series)

    print(time_series.values)
    msg_time_series = []
    # loop over MSG files
    for msg in msg_files:
        print(os.path.basename(msg))

        # read MSG data
        msg_data = msg_read.read(msg)

        # select only timestamps that are covered by time series
        msg_time_series.append(msg_data.where(msg_data.time.isin(time_series), drop=True))
    
    #msg_time_series = xr.concat(msg_time_series, dim=['time'])
    # merge separate daily
    msg_time_series = xr.merge(msg_time_series)
    break
    get_closest_msg_timestamp(mwcch_end)

    # get corresponding MSG timestamp
    msg_data = msg_read.read(msg_file)

    print(msg_data)

    if isinstance(msg_file, list):
        for msg in msg_file:
            print(os.path.basename(msg))
    else:
        print(os.path.basename(msg_file))



# %%
