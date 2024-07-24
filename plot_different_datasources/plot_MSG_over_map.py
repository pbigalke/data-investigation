## using conda environment "my_satpy_env"

# %%
# import packages
import os
import sys
sys.path.append("..")
# import my own script
import readers.read_MSG as msg
import helpers.helper_conversions as hlp
from config.domain_info import domain_DE_CA, domain_expats
from plotting.plot_MSG import channels, plot_MSG_over_map
from plotting.mpl_style import CMAP_MSG_COLOR, CMAP_MSG_GREY

# %%
def main():

    msg_path = "/data/sat/msg/rapid_scan/netcdf/noparallax"
    output_path = "/net/merisi/pbigalke/plots/data_investigation/case_study_20220605/MSG_rapidscan/color_masked"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    years = [2022]
    months = [6]
    days = [5]
    msg_res = 5
    # get all msg files in study period
    all_msg_files = msg.get_MSG_files_in_study_period(msg_path, years, months, days)
    print(len(all_msg_files))
    
    # define domain
    domain=domain_DE_CA

    # define channels to plot
    channelname = "IR_108"

    min_val = 200
    max_val = 270

    for f in all_msg_files:
        # read in msg data of that day'
        data_msg = msg.read(f)

        # loop over timestamps
        for timestamp in data_msg.time.values:
            print(timestamp)
            dt = hlp.get_datestring_from_npdatetime(timestamp)

            # get msg data for this timestamp
            msg_lons = data_msg.sel(time=timestamp).lon.values
            msg_lats = data_msg.sel(time=timestamp).lat.values
            msg_tb = data_msg.sel(time=timestamp).IR_108.values

            # define output location and file name
            #out_name = f'{dt}_msg_{channel}_germandomain.png'
            out_name = f'{dt}_msg_{channelname}_color_masked.png'
            
            # plot msg
            title = f'MSG {channels[channelname]} - {dt[:4]}-{dt[4:6]}-{dt[6:8]} {dt[-4:-2]}:{dt[-2:]}'
            plot_MSG_over_map(msg_lons, msg_lats, msg_tb, channelname, 
                      cmap=CMAP_MSG_COLOR, vmin=min_val, vmax=max_val, alpha=0.8, clear_sky_thresh=max_val,
                      domain=domain, transparent=True, title=title, 
                      path_out=None) #os.path.join(output_path, out_name))



# %%
if __name__ == '__main__':
    main()    
    
    
# %%
