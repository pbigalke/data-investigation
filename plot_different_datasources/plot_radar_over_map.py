"""
Code to read and plot the video of 1 dday radar images of rain rates
"""
# %%
import os
import sys
sys.path.append('..')

import readers.read_radar_DWD as rad
import helpers.datetime_helper as hlp
from config.domain_info import domain_DE_CA
from figures.plot_radar import plot_radar_over_map
from figures.mpl_style import CMAP_RADAR_COLOR

# %%
def main():
    # set the day to process
    yy = '2022'
    mm = '06'
    dd = '05'
    date = yy+mm+dd
    
    # define data path
    path_radolan_DE = "/data/trade_pc/radolan_DE_5min_rain_rate/"

    # define output path
    output_path = "/net/merisi/pbigalke/plots/data_investigation/case_study_20220605/radar_DWD"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # read data
    data = rad.read_radar_DWD(path_radolan_DE, date)

    # define min and max values for plotting
    vmin= 0.
    vmax= 10.
    n_levels = 15

    # loop over timestamps
    for timestamp in data.time.values:
        print(timestamp)
        dt = hlp.get_datestring_from_npdatetime(timestamp)

        # plot rain rate as filled contours
        lats = data.sel(time=timestamp).lat.values
        lons = data.sel(time=timestamp).lon.values
        RR = data.sel(time=timestamp).RR.values

        # define output location and file name
        #out_name = f'{dt}_msg_{channel}_germandomain.png'
        out_name = f'{dt}_radar_DWD.png'
        
        # plot msg
        title = f'{dt[:4]}-{dt[4:6]}-{dt[6:8]} {dt[-4:-2]}:{dt[-2:]}'
        plot_radar_over_map(lats, lons, RR, cmap=CMAP_RADAR_COLOR, vmin=vmin, vmax=vmax, n_levels=n_levels, 
                      domain=domain_DE_CA, transparent=True, title=title,
                        path_out=os.path.join(output_path, out_name))
        

if __name__ == "__main__":
    main()
# %%
