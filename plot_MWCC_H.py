## using conda environment "my_satpy_env"

# %%
# import packages
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs                   # import projections
import cartopy.feature as cfeature           # import features
import os

# import my own script
import readers.read_MWCC_H as mwcc

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


# %%
def _plot_msg_radiances(ax, msg_lons, msg_lats, msg_radiances, transform=ccrs.PlateCarree(), cbar_loc='left'):
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
    # Zm = np.ma.masked_where(np.isnan(msg_radiances), msg_radiances)
    Zm = np.ma.masked_invalid(msg_radiances)
    # plot data with colormap
    pc = ax.pcolormesh(xs, ys, Zm, cmap='Greys', transform=transform)

    # setup colorbar  
    cbar_msg = plt.colorbar(pc,ax=ax,shrink=0.74, location=cbar_loc)
    cbar_msg.set_label('radiances',fontsize=14)
    cbar_msg.ax.tick_params(labelsize=14)


def _plot_mwcch(ax, mwcc_lons, mwcc_lats, mwcc_poh, projection=ccrs.PlateCarree(), cbar_loc='right'):
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
    # define levels for contour plot and colors for colobar
    levels = [.1, .15, .2, .25, .3, .36, .4, .5, .6, .7, .8, .9, 1]
    levels_str = ['0.1', '0.15', '0.2', '0.25', '0.3', '0.36', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1'] # first level: 0, color: '#F5F5F5'
    colors = ['#E3E3E3', '#C4C4C4', '#B0B0B0', '#9E9E9E', '#858585', 
              '#98F5FF', '#00EEEE', '#008B8B', '#000080', 
              '#00FF00', '#FFFF00', '#FF0000']
    
    # mask nan values and plot hail probability contours
    z = np.ma.masked_invalid(mwcc_poh)
    ax.tricontour(mwcc_lons, mwcc_lats, z, levels=levels, linewidths=0.5, colors='k', projection=projection, vmin=0, vmax=1)
    cntr2 = ax.tricontourf(mwcc_lons, mwcc_lats, z, levels=levels, colors=colors, projection=projection, vmin=0, vmax=1)

    # setup colorbar
    cbar = plt.colorbar(cntr2, ax=ax, shrink=0.74, ticks=levels, location=cbar_loc)
    cbar.set_label('probability of hail',fontsize=14)
    cbar.ax.set_yticklabels(levels_str)
    cbar.ax.tick_params(labelsize=14)


def _format_axes(ax):
    """ format axis

    Parameters
    ----------
    ax : cartopy axis
        current axis that is to be formated
    """
    ax.spines["top"].set_linewidth(3)
    ax.spines["right"].set_linewidth(3)
    ax.spines["bottom"].set_linewidth(3)
    ax.spines["left"].set_linewidth(3)

    # draw ticks and labels TODO: doesn't show ticks and labels - find out why!
    ax.tick_params(axis='both',which='major',labelsize=14)
    ax.set_xlabel('Latitude [$^{\circ}$]')
    ax.set_ylabel('Longitude [$^{\circ}$]')
    ax.tick_params(which='minor', length=5, width=2)
    ax.tick_params(which='major', length=7, width=3)
    

def plot_mwcch_over_MSG_radiances(mwcc_lons, mwcc_lats, mwcc_poh, msg_lons, msg_lats, msg_radiances,
                                  extent=None, projection=ccrs.PlateCarree(), transform=ccrs.PlateCarree(), 
                                  title=None, path_out=None):
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
    fig = plt.figure(figsize=(14,10))
    ax = fig.add_subplot(1, 1, 1, projection=projection)

    # set plotting extent and title
    if extent is not None:
        ax.set_extent([extent[0], extent[1], extent[2], extent[3]])
    if title is not None:
        ax.set_title(title)
    
    # cartopy features 
    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.5, color='k')
    ax.add_feature(cfeature.STATES, linewidth=0.2)
    ax.add_feature(cfeature.BORDERS, linewidth=1., color='k')

    # plot msg channel
    _plot_msg_radiances(ax, msg_lons, msg_lats, msg_radiances, transform=transform, cbar_loc='left')
    
    # plot mwcc-h probability of hail
    _plot_mwcch(ax, mwcc_lons, mwcc_lats, mwcc_poh, projection=projection, cbar_loc='right')

    # format axis
    _format_axes(ax)

    # save to file
    if path_out is not None:
        plt.savefig(path_out, bbox_inches='tight', transparent=True)
        print('file saved')
    plt.show()
    plt.close()

# %%
if __name__ == '__main__':
    # example files
    example_mwcch = "mhs_METOPB_20230724-S1905-E2046_056289"
    example_METOPB = "1C-gm.METOPB.MHS.XCAL2016-V.20230724-S190516-E204636.056289.V07A.HDF5"
    example_MSG = "/net/norte/pbigalke/Alps/data/msg/2023-07-24/HRSEVIRI_20230724T193009Z_20230724T194242Z_epct_b890f782_PC.nc"
    
    # define domain
    domain = {"minlon":5., "maxlon":16., "minlat":42., "maxlat":51.5}
    extent=[domain["minlon"], domain["maxlon"], domain["minlat"], domain["maxlat"]]

    # read data from MWCC-H file
    data_mwcc = mwcc.read(example_mwcch, satellite='METOPB', domain=domain)
    mwcc_lons = data_mwcc.lon.values
    mwcc_lats = data_mwcc.lat.values
    mwcc_poh = data_mwcc.POH.values

    # read msg data
    with xr.open_dataset(example_MSG) as dataset:
        print("file read")
        data_msg = dataset

    # loop over all channels
    for ch in np.arange(1, 12, 1):

        print('plot channel ', ch)
        msg_radiances = data_msg[f"channel_{ch}"].values
        msg_lons = data_msg.lon.values
        msg_lats = data_msg.lat.values

        # define output location and file name
        output_path = "output"
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        out_name = f'test_msg_ch{ch}_poh.png'

        # plot msg and poh
        title = f'2023-07-24 19:42 : MSG - {channel_names[f"{ch}"]}'
        plot_mwcch_over_MSG_radiances(mwcc_lons, mwcc_lats, mwcc_poh, msg_lons, msg_lats, msg_radiances,
                                      title=title, path_out=os.path.join(output_path, out_name))
        break

    
# %%
