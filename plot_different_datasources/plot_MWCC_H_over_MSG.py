## using conda environment "my_satpy_env"

# %%
# import packages
import os
import numpy as np
import glob
import sys
import matplotlib.pyplot as plt
import matplotlib as mpl
sys.path.append("..")
# import my own script
from config.domain_info import domain_expats
import readers.read_processed_MWCC_H as mwcc
import readers.read_MSG as msg
import helpers.helper_conversions as hlp
import matching_data.collect_matching_files as fls
import plotting.plot_MWCC_H as mwcc_plt
from plotting.mpl_style import CMAP_MSG_GREY

# %%
# sample the colormaps that you want to use. Use 128 from each so we get 256
# colors in total
def create_combined_colormap(vmin, center, vmax, diverg_cmap=mpl.cm.seismic):
    print(vmin, center, vmax)
    # get number of colors above and below center point representing the respective range percentages
    n_pos = int(265*(vmax-center)/(vmax-vmin))
    n_neg = int(265*(center-vmin)/(vmax-vmin))
    print(n_pos, n_neg)

    # sample colors
    colors_pos = diverg_cmap(np.linspace(0.7, 1, n_pos))
    colors_neg = diverg_cmap(np.linspace(0, 0.5, n_neg))

    # combine them and build a new colormap
    colors = np.vstack((colors_neg, colors_pos))
    return mpl.colors.LinearSegmentedColormap.from_list('recentered_cmap', colors)

# %%

def main():

    mwcch_path = "/net/merisi/pbigalke/data/MWCC-H/netcdf"
    # msg_path = "/data/sat/msg/rapid_scan/netcdf/noparallax"
    msg_path = "/data/sat/msg/netcdf/parallax"

    output_path = "/net/merisi/pbigalke/plots/data_investigation/case_study_20220605/MSG_MWCCH/expats_domain"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    years = [2022]
    months = [6]
    days = [5]
    msg_res = 15
    domain = domain_expats
    
    # collect all files in study period
    all_mwcch_files = fls.get_files_in_study_period(mwcch_path, years, months=months, days=days)
    all_msg_files = fls.get_msg_daily_files_in_study_period(msg_path, years, months=months, days=days)
    print(f"{len(all_msg_files)} MSG files and {len(all_mwcch_files)} MWCC-H files")

    # define channels to plot
    channels = ["WV_062-IR_108", "IR_108", "IR_087"]

    # loop over channels
    for channel in channels[1:-1]:
        print(channel)
        path_channel = f"{output_path}/{channel}"
        if not os.path.exists(path_channel):
            os.makedirs(path_channel)

        # loop over msg files
        for f in all_msg_files[:1]:
            # read in msg data of that day
            data_msg = msg.read(f)

            # get msg data for this timestamp
            msg_lons = data_msg.lon.values
            msg_lats = data_msg.lat.values
            if "-" in channel:
                chan1 = channel.split("-")[0]
                chan2 = channel.split("-")[1]
                print(chan1, chan2)
                msg_tb = data_msg[chan1] - data_msg[chan2]
            else:
                msg_tb = data_msg[channel]

            # get range of values
            min_val = np.nanpercentile(msg_tb.values, 1) # np.nanmin(msg_tb.values)
            max_val = np.nanpercentile(msg_tb.values, 99) # np.nanmax(msg_tb.values)

            # set colormap according to channel
            if "-" in channel:
                cmap = create_combined_colormap(min_val, 0, max_val, diverg_cmap=mpl.cm.seismic)
            else:
                cmap = CMAP_MSG_GREY

            # loop over timestamps
            for timestamp in data_msg.time.values:
                dt = hlp.get_datetimestring_from_npdatetime(timestamp)

                # check if mwcch file is in this timestamp
                mwcc_files = fls.get_file_at_msg_timestamp(mwcch_path, timestamp, msg_res=msg_res)

                # read data from MWCC-H file if there is any
                data_mwcc = mwcc.read(mwcc_files[0]) if len(mwcc_files) > 0 else None
                mwcc_lons = data_mwcc.lon.values if len(mwcc_files) > 0 else None
                mwcc_lats = data_mwcc.lat.values if len(mwcc_files) > 0 else None
                mwcc_poh = data_mwcc.POH.values if len(mwcc_files) > 0 else None
                sat = f"_{mwcc.get_sat_from_filepath(mwcc_files[0])}" if len(mwcc_files) > 0 else ""

                # get msg data for this timestamp
                msg_tb_t = msg_tb.sel(time=timestamp).values

                # define output location and file name
                out_name = f'{path_channel}/{dt}_msg_{channel}_poh{sat}.png'

                # plot msg and poh
                title = f'{dt[:4]}-{dt[4:6]}-{dt[6:8]} {dt[-4:-2]}:{dt[-2:]}'
                mwcc_plt.plot_mwcch_over_MSG(msg_lons, msg_lats, msg_tb_t, channel, 
                                            mwcc_lons=mwcc_lons, mwcc_lats=mwcc_lats, mwcc_poh=mwcc_poh, 
                                            cmap=cmap, vmin=min_val, vmax=max_val, alpha_mwcch=0.6, 
                                            domain=domain, title=title, path_out=out_name)
    
# %%
if __name__ == "__main__":
    tb = main()

# %%
