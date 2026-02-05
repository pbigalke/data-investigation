# Script to plot example MSG and EUCLID data and create gifs

# %%
import os
import glob
import numpy as np
import sys
import pandas as pd
import xarray as xr 
sys.path.append("/home/pbigalke/Documents/Code/data-investigation/data-investigation/")

import plotting_helpers.plot_MSG as msg
import plotting_helpers.plot_EUCLID as eu
import helpers.datetime_helper as hlp
from plotting_helpers.gif_maker import gif_maker, convert_gifs_to_mp4

# %%
def make_msg_plots(example_msg, plot_path_msg, channelname, vmin, vmax):
    # read msg data
    data_msg = xr.open_dataset(example_msg)
    # loop over timestamps
    for timestamp in data_msg.time.values:
        print(timestamp)
        dt = hlp.get_datetimestring_from_npdatetime(timestamp)

        # get msg data for this timestamp
        msg_lons = data_msg.sel(time=timestamp).lon.values
        msg_lats = data_msg.sel(time=timestamp).lat.values
        msg_tb = data_msg.sel(time=timestamp).IR_108.values
        
        # plot msg
        title = f'MSG {channelname} - {dt[:4]}-{dt[4:6]}-{dt[6:8]} {dt[-4:-2]}:{dt[-2:]}'
        msg.plot_MSG_over_map(msg_lons, msg_lats, msg_tb, channelname, 
                    vmin=vmin, vmax=vmax, alpha=0.8, title=title, path_out=f"{plot_path_msg}/msg_{dt}.png")

# %%
def make_euclid_plots(example_euclid, plot_path_euclid, vmin=1, vmax=20, regrid=True, resample=True):
    # read msg data
    data_euclid = xr.open_dataset(example_euclid)

    if resample:
        # resample and sum over 15 min intervals
        data_euclid = data_euclid.resample(time='15Min').sum(dim='time')
    
    # loop over timestamps
    for timestamp in data_euclid.time.values:
        dt = hlp.get_datetimestring_from_npdatetime(timestamp)

        if regrid:
            # get regridded data for this timestamp
            lons = data_euclid.sel(time=timestamp).lon.values
            lats = data_euclid.sel(time=timestamp).lat.values
            euclid_data = data_euclid.sel(time=timestamp).euclid_msg_grid.values

        else:
            # get euclid data for this timestamp
            lons = data_euclid.sel(time=timestamp).euclid_lon.values
            lats = data_euclid.sel(time=timestamp).euclid_lat.values
            euclid_data = data_euclid.sel(time=timestamp).euclid.values

        # plot euclid
        title = "regridded " if regrid else ""
        title += f'EUCLID over MSG - {dt[:4]}-{dt[4:6]}-{dt[6:8]} {dt[-4:-2]}:{dt[-2:]}'
        filename = "euclid"
        if regrid:
            filename += "_regrid"
        if resample:
            filename += "_resample"
        filename += f"_{dt}.png"
        eu.plot_euclid_over_map(lons, lats, euclid_data, vmin=vmin, vmax=vmax, title=title, 
                                path_out=os.path.join(plot_path_euclid, filename))

# %%
def plot_euclid_over_msg(example_euclid, example_msg, plot_path, channelname, vmin_msg, vmax_msg, 
                         cmap_euclid, vmin_euclid, vmax_euclid, alpha_euclid, regrid=True, resample=True):
    # read euclid data
    data_euclid = xr.open_dataset(example_euclid)

    if resample:
        # resample and sum over 15 min intervals
        data_euclid = data_euclid.resample(time='15Min').sum(dim='time')

    # read msg data
    data_msg = xr.open_dataset(example_msg)

    # loop over timestamps
    for timestamp in data_euclid.time.values:
        dt = hlp.get_datetimestring_from_npdatetime(timestamp)

        # get msg data for this timestamp if not resampled round down to next 15 min timestamp
        msg_timestamp = timestamp
        if not resample:
            msg_timestamp -= np.timedelta64(timestamp.astype('datetime64[m]').astype(int) % 15, 'm')

        msg_lons = data_msg.sel(time=msg_timestamp).lon.values
        msg_lats = data_msg.sel(time=msg_timestamp).lat.values
        msg_tb = data_msg.sel(time=msg_timestamp).IR_108.values

        # get euclid data for this timestamp
        if regrid:
            # get regridded data for this timestamp
            euclid_lons = data_euclid.sel(time=timestamp).lon.values
            euclid_lats = data_euclid.sel(time=timestamp).lat.values
            euclid_data = data_euclid.sel(time=timestamp).euclid_msg_grid.values

        else:
            # get euclid data for this timestamp
            euclid_lons = data_euclid.sel(time=timestamp).euclid_lon.values
            euclid_lats = data_euclid.sel(time=timestamp).euclid_lat.values
            euclid_data = data_euclid.sel(time=timestamp).euclid.values

        # plot euclid
        title = "regridded " if regrid else ""
        title += f'EUCLID over MSG - {dt[:4]}-{dt[4:6]}-{dt[6:8]} {dt[-4:-2]}:{dt[-2:]}'
        filename = "euclid_over_msg"
        if regrid:
            filename += "_regrid"
        if resample:
            filename += "_resample"
        filename += f"_{dt}.png"
        eu.plot_euclid_over_MSG(msg_lons, msg_lats, msg_tb, channelname, 
                            euclid_lons=euclid_lons, euclid_lats=euclid_lats, euclid_data=euclid_data, 
                            vmin_msg=vmin_msg, vmax_msg=vmax_msg, 
                            cmap_euclid=cmap_euclid, vmin_euclid=vmin_euclid, vmax_euclid=vmax_euclid, alpha_euclid=alpha_euclid,
                            title=title, path_out=f"{plot_path}/{filename}",)

    

# %%
# define channels to plot
plot_path = "/home/pbigalke/Documents/Code/Repos/EUCLID_preprocessing/plots"
channelname = "IR_108"
min_val = 200
max_val = 300

cmap_euclid = 'RdPu'
vmin_euclid = 1
vmax_euclid = 20
alpha_euclid = 1.0

over_msg = False

days = ["20230724"]  # ["20220817", "20220818", "20220819"] #  #, 

# %%
for day in days:
    print(f"\nprocessing day {day}\n", flush=True)
    # define path to example files of given day
    example_msg = f"/data/sat/msg/netcdf/parallax/{day[:4]}/{day[4:6]}/{day}-EXPATS-RG.nc"
    example_euclid = f"/net/merisi/pbigalke/data/EUCLID/{day[:4]}/{day[4:6]}/EUCLID_total_lightning_{day}.nc"
    
    if not os.path.exists(example_euclid):
        # go to tar file and extract
        example_tar = f"/net/merisi/pbigalke/data/EUCLID/all_years_tar_files/{day[:4]}.tar"
        os.system(f"tar -xvf {example_tar} -C /net/merisi/pbigalke/data/EUCLID/")

    # # plot only MSG
    # plot_path_msg = f"{plot_path}/msg/{day}"
    # os.makedirs(plot_path_msg, exist_ok=True)
    # make_msg_plots(example_msg, plot_path_msg, channelname=channelname, vmin=min_val, vmax=max_val)
    # 
    # # get all images in this folder
    # msg_imgs = sorted(glob.glob(os.path.join(plot_path_msg, '*.png')))
    # print(f"making a gif from {len(msg_imgs)} MSG images.")
    # msg_gif_path = f"{plot_path}/{day}_msg.gif"
    # gif_maker(msg_imgs, msg_gif_path, sec_per_frame=6)

    # euclid data 
    # resample = if euclid data is resampled to MSG temporal resolution
    # regrid = if euclid data is regridded to MSG spatial grid
    for resample in [False, True]:
        for regrid in [False, True]:
            print(f"resample={resample}, regrid={regrid}\n", flush=True)

            # get correct folder path
            if over_msg:
                plot_path_euclid = f"{plot_path}/euclid"
            else:
                plot_path_euclid = f"{plot_path}/euclid_only"
            if resample:
                plot_path_euclid += "/res_15min"
            else:
                plot_path_euclid += "/res_5min"
            if regrid:
                plot_path_euclid += "/msg_grid"
            else:
                plot_path_euclid += "/euclid_grid"
            plot_path_euclid += f"/{day}"
            os.makedirs(plot_path_euclid, exist_ok=True)

            # plot all timestamps as png
            print("plotting all timestamps\n", flush=True)
            if over_msg:
                plot_euclid_over_msg(example_euclid, example_msg, plot_path_euclid, 
                                    channelname=channelname, vmin_msg=min_val, vmax_msg=max_val, 
                                    cmap_euclid=cmap_euclid, vmin_euclid=vmin_euclid, vmax_euclid=vmax_euclid, alpha_euclid=alpha_euclid, 
                                    resample=resample, regrid=regrid)
            else:
                # plot euclid only
                make_euclid_plots(example_euclid, plot_path_euclid, vmin=vmin_euclid, vmax=vmax_euclid, 
                                  regrid=regrid, resample=resample)

            # get all img paths in this folder
            eu_msg_imgs = sorted(glob.glob(os.path.join(plot_path_euclid, f'*.png')))
            print(f"making a gif from {len(eu_msg_imgs)} EUCLID and MSG images.", flush=True)

            # define filename for gif
            filename = f"{day}_euclid"
            if over_msg:
                filename += "_over_msg"
            if regrid:
                filename += "_regrid"
            if resample:
                filename += "_resample"
            euclid_gif_path = f"{plot_path}/{filename}.gif"

            # create gif
            gif_maker(eu_msg_imgs, euclid_gif_path, sec_per_frame=6 if resample else 2)


# %%
# convert all gifs to mp4
print("converting all gifs to mp4")
convert_gifs_to_mp4(plot_path, plot_path)
# %%
