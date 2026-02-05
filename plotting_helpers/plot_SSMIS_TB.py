## using conda environment "my_satpy_env"

# %%
# import packages
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.gridspec import GridSpec
import sys

sys.path.append('..')
from config. domain_info import domain_expats
from plotting_helpers.mpl_style import LABELSIZE, TICKSIZE, TRANSFORM
from plotting_helpers.plot_orography_and_map import draw_map, draw_grid


# %%
def draw_ssmis_colorbar(fig, ax, cmap=mpl.cm.inferno, vmin=None, vmax=None,
                        orientation='vertical', tick_position='right'):

    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    cbar = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
                 cax=ax, orientation=orientation, shrink=0.6)

    label = 'brightness temperature [K]'
    cbar.set_label(label, fontsize=LABELSIZE)
    cbar.ax.tick_params(labelsize=TICKSIZE)
    ax.yaxis.set_ticks_position(tick_position)
    ax.yaxis.set_label_position(tick_position)
    
def plot_ssmis_data(ax, ssmis_lons, ssmis_lats, ssmis_data, cmap=mpl.cm.inferno, \
                    vmin=None, vmax=None, alpha=1., transform=TRANSFORM):
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
    # # mask nan values
    # lon_masked = np.ma.masked_invalid(ssmis_lons).flatten()
    # lat_masked = np.ma.masked_invalid(ssmis_lats).flatten()

    # indices of values that are not nan
    indices_nonmask = np.invert(np.isnan(ssmis_lons.flatten())) # and np.invert(np.isnan(ssmis_lats.flatten()))
    print("indices;", indices_nonmask)

    # only keep non nan values
    lon_clean = ssmis_lons.flatten()[indices_nonmask]
    lat_clean = ssmis_lats.flatten()[indices_nonmask]
    ssmis_clean = ssmis_data.flatten()[indices_nonmask]
    ssmis_masked = np.ma.masked_invalid(ssmis_clean)

    # draw triangular grid density plot
    pc = ax.tripcolor(lon_clean, lat_clean, ssmis_masked, cmap=cmap, vmin=vmin, vmax=vmax, alpha=alpha, transform=transform)
    # pc = ax.scatter(ssmis_lons, ssmis_lats, ssmis_data, cmap=cmap, vmin=vmin, vmax=vmax)
    return pc

def plot_SSMIS_over_map(ssmis_lons, ssmis_lats, ssmis_data,
                      cmap=mpl.cm.Greys, vmin=None, vmax=None, alpha=1.0,
                      domain=domain_expats, projection=TRANSFORM, transform=TRANSFORM, 
                      transparent=True, title=None, path_out=None):
    """ plot MSG brightness temp or reflectance

    Parameters
    ----------
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
    gs = GridSpec(3, 2, figure=fig, width_ratios=[0.95, 0.05], height_ratios=[0.1, 0.8, 0.1])
    ax_plot = fig.add_subplot(gs[:, 0], projection=projection)
    ax_cbar_msg = fig.add_subplot(gs[1, 1])
    
    # draw map
    draw_map(ax_plot, extent=domain, cities=False)

    # draw grid    
    draw_grid(ax_plot)

    # plot msg channel
    plot_ssmis_data(ax_plot, ssmis_lons, ssmis_lats, ssmis_data,
                  cmap=cmap, vmin=vmin, vmax=vmax, alpha=alpha, transform=transform)

    # draw MSG colorbar
    draw_ssmis_colorbar(fig, ax_cbar_msg, cmap=cmap, vmin=vmin, vmax=vmax,
                        orientation='vertical', tick_position='right')
    
    # set title
    if title is not None:
         ax_plot.set_title(title, fontsize=LABELSIZE)
    
    # save to file
    if path_out is not None:
        plt.savefig(path_out, bbox_inches='tight', transparent=transparent)
        plt.close()
        print('file saved')
    else:
        plt.show()
        plt.close()

    
# %%
