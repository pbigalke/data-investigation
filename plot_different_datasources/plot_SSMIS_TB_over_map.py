## using conda environment "my_satpy_env"

# %%
# import packages
import os
import numpy as np
import sys
sys.path.append("..")
# import my own script
import readers.read_processed_SSMIS_TB as ssmis
import helpers.datetime_helper as hlp
from config.domain_info import domain_expats
from figures.plot_SSMIS_TB import plot_SSMIS_over_map
from figures.mpl_style import CMAP_SSMIS_COLOR

def get_vmin_vmax_for_channel():
    return

# %%
def main():

    ssmis_path = "/net/merisi/pbigalke/data/CMSAF_SSMIS_processed"
    output_path = "/net/merisi/pbigalke/plots/data_investigation/case_study_20220605/CMSAF_SSMIS"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    years = [2022]
    months = [6]
    days = [5]

    # get all msg files in study period
    all_files = ssmis.get_files_in_study_period(ssmis_path, years, months, days)
    
    # define domain
    domain=domain_expats

    for f in all_files:
        print(f)
        # read in msg data of that day'
        data_ssmis = ssmis.read(f)
        #print(data_ssmis)

        for ch in data_ssmis.scene_channel.values:
            
            # select channel data
            data_channel = data_ssmis.sel(scene_channel=ch)
            #print(data_channel)

            # get msg data for this timestamp
            ssmis_lons = data_channel.lon.values
            ssmis_lats = data_channel.lat.values
            ssmis_tb = data_channel.tb.values

            # get min and max values for plotting
            # min_val = np.nanmin(ssmis_tb)  # 150
            # max_val = np.nanmax(ssmis_tb)  # 280
            min_val = 150
            max_val = 280

            # get start datetime
            dt = hlp.get_datetimestring_from_npdatetime(data_channel.time.values[0])

            # get name of satellite
            sat = f.split('_')[-2]

            # get channel information
            channel = ssmis.channel_info[f"channel_{ch+1}"]

            # define output location and file name
            out_name = f'{dt}_cmsaf_ssmis_{sat}_channel{ch+1}_{min_val}-{max_val}.png'  # 
            
            # plot msg
            title = f"{sat} SSMIS {channel['frequency']} GHz - {dt[:4]}-{dt[4:6]}-{dt[6:8]} {dt[-4:-2]}:{dt[-2:]}"
            plot_SSMIS_over_map(ssmis_lons, ssmis_lats, ssmis_tb,
                      cmap=CMAP_SSMIS_COLOR, vmin=min_val, vmax=max_val, 
                      domain=domain, transparent=True, title=title, 
                      path_out=os.path.join(output_path, out_name))
            




# %%
if __name__ == '__main__':
    main()    
    
    
# %%
