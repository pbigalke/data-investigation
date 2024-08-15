## using conda environment "my_satpy_env"

# %%
# import packages
import os
import numpy as np
import sys
sys.path.append("..")
# import my own script
from config.domain_info import domain_expats
import readers.read_processed_MWCC_H as mwcc
import readers.read_MSG as msg
import helpers.datetime_helper as hlp
import matching_data.collect_matching_files as match
import plotting.plot_MWCC_H as mwcc_plt

# %%
def main_loop_over_MSG():

    # mwcch_path = "/data/sat/products/PMW_sats/MWCCH_hail_probability/netcdf"
    mwcch_path_regrid = "/data/sat/products/PMW_sats/MWCCH_hail_probability/netcdf_MSG_grid"
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
    all_mwcch_files = match.get_files_in_study_period(mwcch_path_regrid, years, months=months, days=days)
    all_msg_files = match.get_msg_daily_files_in_study_period(msg_path, years, months=months, days=days)
    print(f"{len(all_msg_files)} MSG files and {len(all_mwcch_files)} MWCC-H files")

    # define channels to plot
    channels = ["IR_108"]#"WV_062-IR_108", "IR_108", "IR_087"]

    # loop over channels
    for channel in channels:
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

            # loop over timestamps
            for timestamp in data_msg.time.values:
                dt = hlp.get_datetimestring_from_npdatetime(timestamp)

                # check if mwcch file is in this timestamp
                mwcc_files = match.get_file_at_msg_timestamp(mwcch_path_regrid, timestamp, msg_res=msg_res)

                # read data from MWCC-H file if there is any
                data_mwcc = mwcc.read(mwcc_files[0]) if len(mwcc_files) > 0 else None
                mwcc_lons = data_mwcc.lon.values if len(mwcc_files) > 0 else None
                mwcc_lats = data_mwcc.lat.values if len(mwcc_files) > 0 else None
                mwcc_poh = data_mwcc.POH.values if len(mwcc_files) > 0 else None
                sat = f"_{mwcc.get_sat_from_mwcch_filepath(mwcc_files[0])}_regrid" if len(mwcc_files) > 0 else ""

                # get msg data for this timestamp
                msg_tb_t = msg_tb.sel(time=timestamp).values

                # define output location and file name
                out_name = f'{path_channel}/{dt}_msg_{channel}_poh{sat}.png'

                # plot msg and poh
                title = f'{dt[:4]}-{dt[4:6]}-{dt[6:8]} {dt[-4:-2]}:{dt[-2:]}'
                mwcc_plt.plot_mwcch_over_MSG(msg_lons, msg_lats, msg_tb_t, channel, 
                                            mwcc_lons=mwcc_lons, mwcc_lats=mwcc_lats, mwcc_poh=mwcc_poh, 
                                            vmin=min_val, vmax=max_val, alpha_mwcch=0.6, 
                                            domain=domain, title=title, path_out=out_name)
    
# %%
def main_loop_over_MWCCH(regrid=True):

    if regrid:
        mwcch_path = "/data/sat/products/PMW_sats/MWCCH_hail_probability/netcdf_MSG_grid"
    else:
        mwcch_path = "/data/sat/products/PMW_sats/MWCCH_hail_probability/netcdf"

    output_path = "/net/merisi/pbigalke/plots/data_investigation/case_study_20220605/MSG_MWCCH/expats_domain"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    years = [2022]
    months = [6]
    days = [5]
    msg_res = 15
    domain = domain_expats
    
    # collect all files in study period
    all_mwcch_files = match.get_files_in_study_period(mwcch_path, years, months=months, days=days)

    # define channels to plot
    channels = ["IR_108"]#"WV_062-IR_108", "IR_108", "IR_087"]

    # loop over MWCCH files
    for mwcch_file in all_mwcch_files:

        # get timestamps of MWCCH overpass
        start_dt, end_dt = mwcc.get_start_and_end_datetimes_from_mwcch_filepath(mwcch_file)

        # read data from MWCC-H file if there is any
        data_mwcc = mwcc.read(mwcch_file)
        mwcc_lons = data_mwcc.lon.values
        mwcc_lats = data_mwcc.lat.values
        mwcc_poh = data_mwcc.POH.values
        suffix = f"_{mwcc.get_sat_from_mwcch_filepath(mwcch_file)}"
        if regrid: suffix += "_regrid"

        # get msg data for closest MSG timestamp
        msg_file, msg_dt = match.get_closest_MSG_file_and_timestamp(end_dt, msg_res=msg_res)

        # read in msg data of that day and select data of this timestamp
        data_msg = msg.read(msg_file)

        # loop over channels
        for channel in channels:
            print(channel)
            path_channel = f"{output_path}/{channel}"
            if not os.path.exists(path_channel):
                os.makedirs(path_channel)

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

            # get data of this timestamp
            msg_tb_t = msg_tb.sel(time=msg_dt).values
            dt = hlp.get_datetimestring_from_npdatetime(msg_dt)

            for mwcch_mode in ['poh', 'hail_class']:
                # define output location and file name
                out_name = f'{path_channel}/{dt}_msg_{channel}_{mwcch_mode}{suffix}.png'

                # plot msg and poh
                title = f'{dt[:4]}-{dt[4:6]}-{dt[6:8]} {dt[-4:-2]}:{dt[-2:]}'
                mwcc_plt.plot_mwcch_over_MSG(msg_lons, msg_lats, msg_tb_t, channel, 
                                            mwcc_lons=mwcc_lons, mwcc_lats=mwcc_lats, mwcc_poh=mwcc_poh, 
                                            vmin=min_val, vmax=max_val, alpha_mwcch=0.6, mwcch_mode=mwcch_mode,
                                            domain=domain, title=title, path_out=out_name)
    
# %%
if __name__ == "__main__":
    main_loop_over_MWCCH(regrid=False)

# %%
