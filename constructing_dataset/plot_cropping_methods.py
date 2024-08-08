# %%
import numpy as np
import pandas as pd
import xarray as xr
from scipy import ndimage as ndi
import glob
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.gridspec import GridSpec
import os
import sys
sys.path.append('..')
import readers.read_MSG as msg_read
import readers.read_processed_MWCC_H as mwcch_read
import matching_data.collect_matching_files as match
import helpers.datetime_helper as hlp
import constructing_dataset.crop_time_series_over_hail as tscrop
import plotting.plot_MWCC_H as mwcc_plt
from plotting.mpl_style import LABELSIZE, TICKSIZE, TRANSFORM, CMAP_MSG_GREY
from config.domain_info import domain_expats

# %%
def plot_different_crop_positions(msg_path, mwcch_path, output_path, years, months, days, msg_res):
    n_frames = 1
    cropsize = 128
    channels = {'WV_062-IR_108': {"vmin":-60, "vmax":5}, 
                'IR_108': {"vmin":200, "vmax":280}, 
    }  # 

    # defining colors for crop outlines
    c_hail_area = "gold"
    c_diffWVIR = "cyan"
    c_ot = "red"

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
        msg_data = tscrop.get_MSG_timeseries(msg_path, mwcch_end, msg_res, n_frames)

        # get crop extent over ------------------------------------------------------------------- max hail area
        cg_lon, cg_lat, minlon, maxlon, minlat, maxlat = \
            tscrop.get_crop_extent_over_maxhailarea(msg_data, mwcch_data, cropsize)

        # get crop extent over ------------------------------------------------------------------- diff WV-IR within crop
        cg_lon_diff, cg_lat_diff, minlon_diff, maxlon_diff, minlat_diff, maxlat_diff = \
            tscrop.recenter_crop_over_highest_clouds(msg_data, [minlon, maxlon, minlat, maxlat])

        # get crop extent over ------------------------------------------------------------------- OT area within crop
        cg_lon_OT, cg_lat_OT, minlon_OT, maxlon_OT, minlat_OT, maxlat_OT = \
            tscrop.recenter_crop_over_highest_clouds(msg_data, [minlon, maxlon, minlat, maxlat], mode='OT')

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
                    # --------------------------------------------------------------------- plot crop over max hail area
                    # plot last timestamp with hail area crop
                    dt = hlp.get_datetimestring_from_npdatetime(ts)
                    title = f'crop max hail area, {dt[:4]}-{dt[4:6]}-{dt[6:8]} {dt[-4:-2]}:{dt[-2:]}'
                    outpath = f"{output_path}/crop_over_maxhailarea"
                    if not os.path.exists(outpath): os.makedirs(outpath)
                    outname = f"{outpath}/{dt}_{channel}_crop_over_maxhailarea.png"

                    # plot crops over MSG and MWCC-H
                    mwcc_plt.plot_mwcch_over_MSG(msg_data.lon.values, msg_data.lat.values, msg_tb.sel(time=ts), channel, 
                                                mwcch_data.lon.values, mwcch_data.lat.values, mwcch_data.POH.values, 
                                                mark_points=[[cg_lon, cg_lat, c_hail_area, 'x']], 
                                                draw_subdomains=[[minlon, maxlon, minlat, maxlat, c_hail_area, '-']], 
                                                vmin=channels[channel]["vmin"], vmax=channels[channel]["vmax"], 
                                                title=title, path_out=outname)

                    # --------------------------------------------------------------------- plot different ways of cropping
                    # plot last timestamp with hail area crop
                    dt = hlp.get_datetimestring_from_npdatetime(ts)
                    title = f'crop max hail area, {dt[:4]}-{dt[4:6]}-{dt[6:8]} {dt[-4:-2]}:{dt[-2:]}'
                    outpath = f"{output_path}/try_out_crop_positions"
                    if not os.path.exists(outpath): os.makedirs(outpath)
                    outname = f"{outpath}/{dt}_{channel}_crop_over_maxhailarea_WV-IR_or_OT.png"

                    # plot crops over MSG and MWCC-H
                    mwcc_plt.plot_mwcch_over_MSG(msg_data.lon.values, msg_data.lat.values, msg_tb.sel(time=ts), channel, 
                                                mwcch_data.lon.values, mwcch_data.lat.values, mwcch_data.POH.values, 
                                                mark_points=[[cg_lon, cg_lat, c_hail_area, 'x'], 
                                                            [cg_lon_diff, cg_lat_diff, c_diffWVIR, 'x'], 
                                                            [cg_lon_OT, cg_lat_OT, c_ot, 'x']], 
                                                draw_subdomains=[[minlon, maxlon, minlat, maxlat, c_hail_area, '-'],
                                                                [minlon_diff, maxlon_diff, minlat_diff, maxlat_diff, c_diffWVIR, '-'],
                                                                [minlon_OT, maxlon_OT, minlat_OT, maxlat_OT, c_ot, '-']], 
                                                vmin=channels[channel]["vmin"], vmax=channels[channel]["vmax"], 
                                                title=title, path_out=outname)




# %%
# mwcch_path = "/net/merisi/pbigalke/data/MWCC-H/netcdf"
msg_path = msg_read.MSG_PATH
mwcch_path = mwcch_read.MWCCH_PATH

output_path = "/net/merisi/pbigalke/plots/data_investigation/constructing_dataset/casestudy_20220605"
if not os.path.exists(output_path):
    os.makedirs(output_path)

years = [2022]
months = [6]
days = [5]
msg_res = 15

plot_different_crop_positions(msg_path, mwcch_path, output_path, years, months, days, msg_res)

# %%
