## using conda environment "my_satpy_env"

# %%
# import packages
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import cartopy.crs as ccrs                   # import projections
import cartopy.feature as cfeature           # import features
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import os
import pandas as pd
from matplotlib.gridspec import GridSpec

import sys
sys.path.append("..")
# import my own script
import readers.read_processed_MWCC_H as mwcc
import readers.read_MSG as msg
import helpers.helper_conversions as hlp

# %%
channel_names = {"1": "VIS 0.6", 
                "2": "VIS 0.8", 
                "3": "NIR 1.6", 
                "4": "IR 3.9", 
                "5": "WV 6.2", 
                "6": "WV 7.3", 
                "7": "IR 8.7", 
                "8": "IR 9.7 - O3", 
                "9": "IR 10.8", 
                "10": "IR 12.0", 
                "11": "IR 13.4 - CO2", }

channels = ["IR_016", "IR_039", "IR_087", "IR_097", "IR_108", "IR_120", "IR_134", \
            "VIS006", "VIS008", "WV_062", "WV_073"]

# %%
CMAP_MSG = mpl.cm.Greys
BORDER_COLOR = 'yellow'
LABEL_SIZE = 12
TICK_SIZE = 10

def _get_mwcch_color_levels(with_zero=False):

    levels = [0] if with_zero else []
    colors = ['#F5F5F5'] if with_zero else []

    # define levels for contour plot and ...
    levels.extend([.1, .15, .2, .25, .3, .36, .4, .5, .6, .7, .8, .9, 1])
    # colors for colobar
    colors.extend(['#E3E3E3', '#C4C4C4', '#B0B0B0', '#9E9E9E', '#858585', 
              '#98F5FF', '#00EEEE', '#008B8B', '#000080', 
              '#00FF00', '#FFFF00', '#FF0000'])

    return levels, colors

def _draw_mwcch_colorbar(fig, ax, orientation='vertical'):

    levels, colors = _get_mwcch_color_levels(with_zero=True)
    cmap = mpl.colors.ListedColormap(colors)
    norm = mpl.colors.BoundaryNorm(levels, cmap.N)
    cbar = fig.colorbar(mpl.cm.ScalarMappable(cmap=cmap, norm=norm),
                        cax=ax, orientation=orientation,
                        spacing='uniform',
                        #label='probability of hail',
                        ticks=levels)

    cbar.ax.set_yticklabels([f'{l:g}' for l in levels])
    cbar.set_label('probability of hail', fontsize=LABEL_SIZE)
    cbar.ax.tick_params(labelsize=TICK_SIZE)

def _draw_msg_colorbar(fig, ax, label, vmin=None, vmax=None, orientation='vertical'):

    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    cbar = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=CMAP_MSG),
                 cax=ax, orientation=orientation, )
                 #label=label)

    cbar.set_label(label, fontsize=LABEL_SIZE)
    cbar.ax.tick_params(labelsize=TICK_SIZE)
    ax.yaxis.set_ticks_position('left')
    ax.yaxis.set_label_position('left')

def _format_map_plot(ax, extent, title=None):
    #set axis thick labels
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                    linewidth=0.75, color='gray', alpha=0.6, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False
    gl.xlines = True
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'size': TICK_SIZE, 'color': 'black'}
    gl.ylabel_style = {'size': TICK_SIZE, 'color': 'black'}

    # Adds coastlines and borders to the current axes
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.5, color=BORDER_COLOR)
    ax.add_feature(cfeature.STATES, linewidth=0.2)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5, color=BORDER_COLOR)

    # set extent and add title
    ax.set_extent(extent) #[left, right, bottom ,top]
    ax.set_title(title, fontsize=LABEL_SIZE)

# %%
def _plot_msg_data(ax, msg_lons, msg_lats, msg_tb, vmin=None, vmax=None, transform=ccrs.PlateCarree()):
    """ plot the given msg channel as pcolormesh

    Parameters
    ----------
    ax : cartopy axis
        current axis on which to plot
    msg_lons : 1d-array {float}
        longitudes of msg grid
    msg_lats : 1d-array {float}
        latitudes of msg grid
    msg_radiances : 2d-array {float} of shape (len(msg_lats), len(msg_lons))
        radiances of msg channel
    transform : cartopy transformation, optional
        transformation in which the data is given, by default ccrs.PlateCarree()
    cbar_loc : str, optional
        location of colorbar on axis, by default 'left'
    """
    # create 2d grid from lons and lats 1d-arrays
    xs, ys = np.meshgrid(msg_lons, msg_lats)
    # mask all nan values in radiances
    Zm = np.ma.masked_invalid(msg_tb)
    # plot data with colormap
    pc = ax.pcolormesh(xs, ys, Zm, cmap=CMAP_MSG, vmin=vmin, vmax=vmax, transform=transform)

    return pc

def _plot_mwcch(ax, mwcc_lons, mwcc_lats, mwcc_poh, projection=ccrs.PlateCarree()):
    """ plot the hail probability of MWCC-H

    Parameters
    ----------
    ax : cartopy axis
        current axis on which to plot
    mwcc_lons : 1d-array {float}
        longitude values of each pixel
    mwcc_lats : 1d-array {float}
        latitude values of each pixel
    mwcc_poh : 1d-array {float}
        probability of hail for each pixel
    projection : cartopy projection, optional
        projection to display data in, by default ccrs.PlateCarree()
    cbar_loc : str, optional
        location of colorbar on axis, by default 'right'
    """

    levels, colors = _get_mwcch_color_levels()
    # mask nan values and plot hail probability contours
    z = np.ma.masked_invalid(mwcc_poh)
    ax.tricontour(mwcc_lons, mwcc_lats, z, levels=levels, linewidths=0.5, colors='k', projection=projection, vmin=0, vmax=1)
    ax.tricontourf(mwcc_lons, mwcc_lats, z, levels=levels, colors=colors, projection=projection, vmin=0, vmax=1)

def plot_mwcch_over_MSG(msg_lons, msg_lats, msg_tb, mwcc_lons=None, mwcc_lats=None, mwcc_poh=None, channelname=None,
                        vmin=None, vmax=None, extent=None, projection=ccrs.PlateCarree(), transform=ccrs.PlateCarree(), 
                        transparent=True, title=None, path_out=None):
    """ plot probability of hail contour over MSG radiances

    Parameters
    ----------
   mwcc_lons : 1d-array {float}
        longitude values of each pixel
    mwcc_lats : 1d-array {float}
        latitude values of each pixel
    mwcc_poh : 1d-array {float}
        probability of hail for each pixel
    msg_lons : 1d-array {float}
        longitudes of msg grid
    msg_lats : 1d-array {float}
        latitudes of msg grid
    msg_radiances : 2d-array {float} of shape (len(msg_lats), len(msg_lons))
        radiances of msg channel
    extent : list(float), optional
        [minlon, maxlon, minlat, maxlat], by default None
    projection : cartopy projection, optional
        projection to display data in, by default ccrs.PlateCarree()
    transform : cartopy transformation, optional
        transformation in which the data is given, by default ccrs.PlateCarree()
    title : string, optional
        title of figure, by default None
    path_out : string or os.path, optional
        complete path to output figure, by default None
    """
    # create figure mit cartopy axis of certain projection
    #fig = plt.figure(figsize=(7,5))

    fig = plt.figure(figsize=(6, 5)) #, layout="constrained")

    # devide figure in axes for colorbars and plot
    gs = GridSpec(3, 4, figure=fig, width_ratios=[0.05, 0.1, 0.8, 0.05], height_ratios=[0.1, 0.8, 0.1])
    ax_cbar_msg = fig.add_subplot(gs[1, 0])
    ax_plot = fig.add_subplot(gs[:, 2], projection=projection)
    ax_cbar_mwcch = fig.add_subplot(gs[1, -1])

    # draw MSG colorbar
    msg_label = 'reflectance' if 'VIS' in channelname else 'brightness temperature'
    _draw_msg_colorbar(fig, ax_cbar_msg, msg_label, vmin=vmin, vmax=vmax, orientation='vertical')

    # draw MWCC-H colorbar
    _draw_mwcch_colorbar(fig, ax_cbar_mwcch, orientation='vertical')

    # format the axis for the map
    _format_map_plot(ax_plot, extent, title=title)

    # plot msg channel
    _plot_msg_data(ax_plot, msg_lons, msg_lats, msg_tb, vmin=vmin, vmax=vmax, transform=transform)
    
    # plot hail probability if not None
    if mwcc_poh is not None and mwcc_lons is not None and mwcc_lats is not None:
        # plot mwcc-h probability of hail
        _plot_mwcch(ax_plot, mwcc_lons, mwcc_lats, mwcc_poh, projection=projection)

    # save to file
    if path_out is not None:
        plt.savefig(path_out, bbox_inches='tight', transparent=transparent)
        plt.close()
        print('file saved')
    else:
        plt.show()
        plt.close()

# %%
if __name__ == '__main__':
    
    mwcch_path = "/net/merisi/pbigalke/data/MWCC-H/netcdf"
    msg_path = "/data/sat/msg/rapid_scan/netcdf/noparallax"
    # msg_path = "/data/sat/msg/netcdf/parallax"

    #output_path = "/net/merisi/pbigalke/plots/data_investigation/case_study_20220605/MSG_MWCCH/expats_domain"
    output_path = "/net/merisi/pbigalke/plots/data_investigation/case_study_20220605/MSG_MWCCH_rapidscan/min200_max280"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    years = [2022]
    months = [6]
    days = [5]
    msg_res = 5
    detectors = ["ATMS", "MHS", "SSMIS"]
    #all_mwcch_files = mwcc.get_mwcch_files_in_study_period(mwcch_path, detectors, years, months, days)
    all_msg_files = msg.get_MSG_files_in_study_period(msg_path, years, months, days)
    #print(all_mwcch_files)
    print(all_msg_files)
    

    # define domain
    expats_domain = {"minlon":5., "maxlon":16., "minlat":42., "maxlat":51.5}
    german_domain_small = {"minlon":8.3, "maxlon":13., "minlat":47.5, "maxlat":49.5}
    german_domain = {"minlon":7.5, "maxlon":13., "minlat":47.5, "maxlat":51.5}
    
    #extent=[expats_domain["minlon"], expats_domain["maxlon"], expats_domain["minlat"], expats_domain["maxlat"]]
    extent=[german_domain["minlon"], german_domain["maxlon"], german_domain["minlat"], german_domain["maxlat"]]

    # define channels to plot
    channel = "IR_108"

    for f in all_msg_files:
        # read in msg data of that day
        data_msg = msg.read(f)

        # get range of values
        min_val = 200  # np.nanmin(data_msg[f"{channel}"].values)
        max_val = 280  # np.nanmax(data_msg[f"{channel}"].values)

        # loop over timestamps
        for timestamp in data_msg.time.values:
            print(timestamp)
            dt = hlp.get_datestring_from_npdatetime(timestamp)

            # check if mwcch file is in this timestamp
            mwcc_files = mwcc.get_mwcch_file_at_msg_timestamp(mwcch_path, detectors, timestamp, msg_res=msg_res)
    
            # read data from MWCC-H file if there is any
            data_mwcc = mwcc.read(mwcc_files[0]) if len(mwcc_files) > 0 else None
            mwcc_lons = data_mwcc.lon.values if len(mwcc_files) > 0 else None
            mwcc_lats = data_mwcc.lat.values if len(mwcc_files) > 0 else None
            mwcc_poh = data_mwcc.POH.values if len(mwcc_files) > 0 else None

            # get msg data for this timestamp
            msg_lons = data_msg.sel(time=timestamp).lon.values
            msg_lats = data_msg.sel(time=timestamp).lat.values
            msg_tb = data_msg.sel(time=timestamp).IR_108.values

            # define output location and file name
            out_name = f'{dt}_msg_{channel}_poh_min{min_val}_max{max_val}.png'

            # plot msg and poh
            title = f'{dt[:4]}-{dt[4:6]}-{dt[6:8]} {dt[-4:-2]}:{dt[-2:]}'
            plot_mwcch_over_MSG(msg_lons, msg_lats, msg_tb, mwcc_lons=mwcc_lons, mwcc_lats=mwcc_lats, mwcc_poh=mwcc_poh, 
                                channelname=channel, vmin=min_val, vmax=max_val, extent=extent, transparent=True, 
                                title=title, path_out=os.path.join(output_path, out_name))


    
# %%
