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
from plotting.mpl_style import LABELSIZE, TICKSIZE, TRANSFORM, CMAP_MSG_GREY
import plotting.plot_orography_and_map as map_plt
import plotting.plot_MSG as msg_plt
from config.domain_info import domain_expats

# %%
def plot_timeseries_examples(timeseries_path, years, months, days, channels, output_path):

    # get all hail classes
    hail_classes = mwcch_read.get_hail_class()

    # loop over hail classes
    for label in hail_classes:

        # get all MSG time series files
        label_timeseries = sorted(glob.glob(f"{timeseries_path}/{label}/*.nc"))

        if len(label_timeseries) > 0:
            # loop over all time series
            for tms in label_timeseries:

                # proceed if file is in study period
                y, m, d = msg_read.get_y_m_d_from_filepath(tms)
                if int(y) in years and int(m) in months and int(d) in days:

                    # read in MSG_timeseries
                    data_timeserie = msg_read.read(tms, channels)

                    # get extent of this crop
                    extent = [np.min(data_timeserie.lon.values), np.max(data_timeserie.lon.values), 
                            np.min(data_timeserie.lat.values), np.max(data_timeserie.lat.values)]

                    # get number of timestamps and channels for plot
                    n_t = data_timeserie.n_frames
                    n_c = len(channels)

                    # define output path
                    path_out = f"{output_path}/{label}"
                    if not os.path.exists(path_out): os.makedirs(path_out)
                    filename = f"{hlp.get_datetimestring_from_npdatetime(data_timeserie.time.values[-1])}.png"

                    # plot 
                    fig = plt.figure(figsize=(n_t*2, n_c*2)) #, layout="constrained")

                    # devide figure in axes for colorbars and plot
                    gs = GridSpec(n_c, n_t, figure=fig)#, width_ratios=[0.05, 0.1, 0.8, 0.05], height_ratios=[0.1, 0.8, 0.1])

                    for t in range(n_t):
                        for c in range(n_c):
                            # get axis 
                            ax = fig.add_subplot(gs[c, t], projection=TRANSFORM)


                            # channel
                            channel = channels[c]

                            # draw map
                            map_plt.draw_map(ax, mode="light", extent=extent, cities=False)

                            # set ticks and title
                            yticks = True if t == 0 else False
                            xticks = True if c == (n_c-1) else False
                            if c == 0:
                                ax.set_title(f"{hlp.get_timestring_from_npdatetime(data_timeserie.time.values[t])}")

                            # draw grid    
                            map_plt.draw_grid(ax, xticks=xticks, yticks=yticks)
                        
                            # set colormap and get data of channel
                            # get msg data for this timestamp
                            msg_lons = data_timeserie.lon.values
                            msg_lats = data_timeserie.lat.values
                            if "-" in channel:
                                chan1 = channel.split("-")[0]
                                chan2 = channel.split("-")[1]
                                msg_tb = data_timeserie[chan1].isel(time=t) - data_timeserie[chan2].isel(time=t)

                                # set colormap
                                cmap = msg_plt.create_WV_IR_diff_colormap(-60, 0, 5)
                            else:
                                msg_tb = data_timeserie[channel].isel(time=t)
                                cmap = CMAP_MSG_GREY

                            # plot msg channel
                            msg_plt.plot_msg_data(ax, msg_lons, msg_lats, msg_tb, cmap=cmap)

                            # mark area of max hail
                            map_plt.mark_point(ax, data_timeserie.hail_area_lon, data_timeserie.hail_area_lat, color='r', marker='x')


                    # set title
                    fig.suptitle(f"{hlp.get_datestring_from_npdatetime(data_timeserie.time.values[-1])} - {label}")
                    
                    # # save to file
                    plt.tight_layout()
                    plt.savefig(os.path.join(path_out, filename), bbox_inches='tight', transparent=True)
                    plt.close()




# %%
# mwcch_path = "/net/merisi/pbigalke/data/MWCC-H/netcdf"
timeseries_path = "/net/merisi/pbigalke/data/MSG_timeseries_maxhailarea"

output_path = "/net/merisi/pbigalke/plots/data_investigation/constructing_dataset/casestudy_20220605/time_series"
if not os.path.exists(output_path):
    os.makedirs(output_path)

years = [2022]
months = [6]
days = [5]
msg_res = 15
channels = ["IR_108", "WV_062", "WV_062-IR_108"]

plot_timeseries_examples(timeseries_path, years, months, days, channels, output_path)

# %%
