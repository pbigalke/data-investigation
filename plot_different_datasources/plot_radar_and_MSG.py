"""
Code to read and plot the video of 1 dday radar images of rain rates
"""
# %%
# import packages
import os
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

import sys
sys.path.append("..")
# import my own script
import readers.read_MSG as msg
import readers.read_radar_DWD as rad
import helpers.datetime_helper as hlp
from config.domain_info import domain_DE_CA
import figures.plot_orography_and_map as plt_map
import figures.plot_MSG as plt_msg
import figures.plot_radar as plt_rad
from figures.mpl_style import CMAP_MSG_COLOR, CMAP_RADAR_COLOR, TRANSFORM, LABELSIZE

# %%
def plot_radar_and_MSG(msg_lons, msg_lats, msg_data, channelname, rad_lons, rad_lats, rad_RR,  
                      cmap_msg=CMAP_MSG_COLOR, vmin_msg=None, vmax_msg=None, alpha_msg=1.0, clear_sky_thresh_msg=None, 
                      cmap_rad=CMAP_RADAR_COLOR, vmin_rad=0, vmax_rad=10, n_levels_rad=15, 
                      domain=domain_DE_CA, projection=TRANSFORM, transform=TRANSFORM, 
                      transparent=True, title=None, path_out=None):
    """ plot MSG brightness temp or reflectance next to radar rainrate
    """
    # create figure mit cartopy axis of certain projection
    #fig = plt.figure(figsize=(7,5))

    fig = plt.figure(figsize=(6, 7)) #, layout="constrained")

    # devide figure in axes for colorbars and plot
    gs = GridSpec(2, 2, figure=fig, width_ratios=[0.95, 0.05], height_ratios=[0.8, 0.8])
    ax_plot_msg = fig.add_subplot(gs[0, 0], projection=projection)
    ax_cbar_msg = fig.add_subplot(gs[0, 1])
    ax_plot_rad = fig.add_subplot(gs[1, 0], projection=projection)
    ax_cbar_rad = fig.add_subplot(gs[1, 1])

    ############################################# MSG plot
    # draw orography
    plt_map.draw_orography_filled(ax_plot_msg)

    # plot msg channel and colorbar
    plt_msg.plot_msg_data(ax_plot_msg, msg_lons, msg_lats, 
                          plt_msg.msg_mask_clouds(msg_data, channelname, clear_sky_thresh_msg) if clear_sky_thresh_msg else msg_data, 
                          cmap=cmap_msg, vmin=vmin_msg, vmax=vmax_msg, alpha=alpha_msg, transform=transform)
    
    # draw map and grid
    plt_map.draw_map(ax_plot_msg, extent=domain)
    plt_map.draw_grid(ax_plot_msg)

    # draw colorbar
    plt_msg.draw_msg_colorbar(fig, ax_cbar_msg, channelname, cmap=cmap_msg, vmin=vmin_msg, vmax=vmax_msg,
                              orientation='vertical', tick_position='right')

    ############################################# radar plot
    # draw orography, map and grid
    plt_map.draw_orography_filled(ax_plot_rad)

    # plot rain rate as filled contours
    plt_rad.plot_radar(ax_plot_rad, rad_lons, rad_lats, rad_RR, 
                       cmap=cmap_rad, vmin=vmin_rad, vmax=vmax_rad, n_levels=n_levels_rad, transform=transform)

    # draw map and grid
    plt_map.draw_map(ax_plot_rad, extent=domain)
    plt_map.draw_grid(ax_plot_rad)

    # draw color bar
    plt_rad.draw_radar_colorbar(fig, ax_cbar_rad, cmap=cmap_rad, vmin=vmin_rad, vmax=vmax_rad, n_levels=n_levels_rad, 
                                orientation='vertical', tick_position='right')
    # set title
    if title is not None:
         ax_plot_msg.set_title(title, fontsize=LABELSIZE)
    
    # save to file
    if path_out is not None:
        plt.savefig(path_out, bbox_inches='tight', transparent=transparent)
        plt.close()
        print('file saved')
    else:
        plt.show()
        plt.close()


# %%
def main():

    # define msg path
    msg_path = "/data/sat/msg/rapid_scan/netcdf/noparallax"
    # define radar path
    path_radolan_DE = "/data/trade_pc/radolan_DE_5min_rain_rate/"
    # define output path
    output_path = "/net/merisi/pbigalke/plots/data_investigation/case_study_20220605/radar_and_MSG"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    # define date
    years = [2022]
    months = [6]
    days = [5]
    date = '20220605'

    # get all msg files in study period
    all_msg_files = msg.get_MSG_files_in_study_period(msg_path, years, months, days)
    print(len(all_msg_files))
    
    # read radar data
    data_rad = rad.read_radar_DWD(path_radolan_DE, date)

    # define domain
    domain=domain_DE_CA

    # define channels to plot
    channelname = "IR_108"

    # define color range
    vmin_msg = 200
    vmax_msg = 270
    clear_sky_thresh_msg = vmax_msg
    vmin_rad = 0.
    vmax_rad = 10.
    n_levels_rad = 15

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

            # get radar data for this timestamp
            rad_lons = data_rad.sel(time=timestamp).lon.values
            rad_lats = data_rad.sel(time=timestamp).lat.values
            rad_RR = data_rad.sel(time=timestamp).RR.values

            # define output location and file name
            #out_name = f'{dt}_msg_{channel}_germandomain.png'
            out_name = f'{dt}_radar_and_msg_{channelname}.png'
            
            # plot radar and msg
            title = f'{dt[:4]}-{dt[4:6]}-{dt[6:8]} {dt[-4:-2]}:{dt[-2:]}'
            plot_radar_and_MSG(msg_lons, msg_lats, msg_tb, channelname, rad_lons, rad_lats, rad_RR,  
                               cmap_msg=CMAP_MSG_COLOR, vmin_msg=vmin_msg, vmax_msg=vmax_msg, clear_sky_thresh_msg=vmax_msg, alpha_msg=0.8,
                               cmap_rad=CMAP_RADAR_COLOR, vmin_rad=vmin_rad, vmax_rad=vmax_rad, n_levels_rad=n_levels_rad, 
                               domain=domain_DE_CA, transparent=True, title=title, path_out=os.path.join(output_path, out_name))

# %%
if __name__ == "__main__":
    main()
# %%
