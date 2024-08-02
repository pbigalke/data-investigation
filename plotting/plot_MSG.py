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
from plotting.mpl_style import LABELSIZE, TICKSIZE, TRANSFORM
from plotting.plot_orography_and_map import draw_orography_filled, draw_map, draw_grid

# %%
channels = {
            "IR_016": r"NIR 1.6 ${\mu}m$",
            "IR_039": r"IR 3.9 ${\mu}m$",
            "IR_087": r"IR 8.7 ${\mu}m$", #
            "IR_097": r"IR 9.7 ${\mu}m$",
            "IR_108": r"IR 10.8 ${\mu}m$", #
            "IR_120": r"IR 12.0 ${\mu}m$",
            "IR_134": r"IR 13.4 ${\mu}m$",
            "VIS006": r"VIS 0.6 ${\mu}m$",
            "VIS008": r"VIS 0.8 ${\mu}m$",
            "WV_062": r"WV 6.2 ${\mu}m$",
            "WV_073": r"WV 7.3 ${\mu}m$",
            "WV_062-IR_108": r"(6.2 -10.8) ${\mu}m$",
}

def create_WV_IR_diff_colormap(vmin, center, vmax, diverg_cmap=mpl.cm.seismic):
    if vmin is None:
        vmin = -1
    if vmax is None:
        vmax = 1

    # get number of colors above and below center point representing the respective range percentages
    n_pos = int(265*(vmax-center)/(vmax-vmin)) if vmax > center else 1
    n_neg = int(265*(center-vmin)/(vmax-vmin)) if vmin < center else 1

    # sample colors
    colors_pos = diverg_cmap(np.linspace(0.7, 1, n_pos))
    colors_neg = diverg_cmap(np.linspace(0, 0.5, n_neg))

    # combine them and build a new colormap
    colors = np.vstack((colors_neg, colors_pos))
    return mpl.colors.LinearSegmentedColormap.from_list('recentered_cmap', colors)

# %%
def draw_msg_colorbar(fig, ax, channelname, cmap=mpl.cm.Greys, vmin=None, vmax=None,
                      orientation='vertical', tick_position='right'):

    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    cbar = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
                 cax=ax, orientation=orientation, shrink=0.6)

    if "-" in channelname:
        label = f"diff {channelname}"
    elif "VIS" in channelname:
        label = f"{channelname} reflectance"
    else:
        label = f'{channelname} Tb [K]'
    cbar.set_label(label, fontsize=LABELSIZE)
    cbar.ax.tick_params(labelsize=TICKSIZE)
    ax.yaxis.set_ticks_position(tick_position)
    ax.yaxis.set_label_position(tick_position)
    
def plot_msg_data(ax, msg_lons, msg_lats, msg_data, cmap=mpl.cm.Greys, \
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
    # create 2d grid from lons and lats 1d-arrays
    xs, ys = np.meshgrid(msg_lons, msg_lats)
    # mask all nan values in radiances
    Zm = np.ma.masked_invalid(msg_data)

    # plot data with colormap
    pc = ax.pcolormesh(xs, ys, Zm, cmap=cmap, vmin=vmin, vmax=vmax, alpha=alpha, transform=transform)

    return pc

def msg_mask_clouds(msg_data, channelname, clear_sky_thresh):
    if "VIS" in channelname:
        return np.ma.masked_less(msg_data, clear_sky_thresh)
    else:
        return np.ma.masked_greater(msg_data, clear_sky_thresh)
    
def plot_MSG_over_map(msg_lons, msg_lats, msg_data, channelname, 
                      cmap=mpl.cm.Greys, vmin=None, vmax=None, alpha=1.0, clear_sky_thresh=None, 
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

    # draw orography
    draw_orography_filled(ax_plot)
    
    # draw map
    draw_map(ax_plot, extent=domain)

    # draw grid    
    draw_grid(ax_plot)

    # plot msg channel
    plot_msg_data(ax_plot, msg_lons, msg_lats, 
                  msg_mask_clouds(msg_data, channelname, clear_sky_thresh) if clear_sky_thresh else msg_data, 
                  cmap=cmap, vmin=vmin, vmax=vmax, alpha=alpha, transform=transform)

    # draw MSG colorbar
    draw_msg_colorbar(fig, ax_cbar_msg, channelname, cmap=cmap, vmin=vmin, vmax=vmax,
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
