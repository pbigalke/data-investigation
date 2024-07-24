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
from plotting.plot_MSG import plot_msg_data, draw_msg_colorbar, msg_mask_clouds


# %%
def get_mwcch_color_levels(with_zero=False):

    levels = [0] if with_zero else []
    colors = ['#F5F5F5'] if with_zero else []

    # define levels for contour plot and ...
    levels.extend([.1, .15, .2, .25, .3, .36, .4, .5, .6, .7, .8, .9, 1])
    # colors for colobar
    colors.extend(['#E3E3E3', '#C4C4C4', '#B0B0B0', '#9E9E9E', '#858585', 
              '#98F5FF', '#00EEEE', '#008B8B', '#000080', 
              '#00FF00', '#FFFF00', '#FF0000'])

    return levels, colors

def draw_mwcch_colorbar(fig, ax, orientation='vertical'):

    levels, colors = get_mwcch_color_levels(with_zero=True)
    cmap = mpl.colors.ListedColormap(colors)
    norm = mpl.colors.BoundaryNorm(levels, cmap.N)
    cbar = fig.colorbar(mpl.cm.ScalarMappable(cmap=cmap, norm=norm),
                        cax=ax, orientation=orientation,
                        spacing='uniform',
                        #label='probability of hail',
                        ticks=levels)

    cbar.ax.set_yticklabels([f'{l:g}' for l in levels])
    cbar.set_label('probability of hail', fontsize=LABELSIZE)
    cbar.ax.tick_params(labelsize=TICKSIZE)

# %%
def plot_mwcch(ax, mwcc_lons, mwcc_lats, mwcc_poh, projection=TRANSFORM):
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

    levels, colors = get_mwcch_color_levels()
    # mask nan values and plot hail probability contours
    z = np.ma.masked_invalid(mwcc_poh)
    ax.tricontour(mwcc_lons, mwcc_lats, z, levels=levels, linewidths=0.5, colors='k', projection=projection, vmin=0, vmax=1)
    ax.tricontourf(mwcc_lons, mwcc_lats, z, levels=levels, colors=colors, projection=projection, vmin=0, vmax=1)

def plot_mwcch_over_MSG(msg_lons, msg_lats, msg_data, channelname, mwcc_lons=None, mwcc_lats=None, mwcc_poh=None, 
                        cmap=mpl.cm.Greys, vmin=None, vmax=None, alpha=1.0, clear_sky_thresh=None, draw_oro=False,
                        domain=domain_expats, projection=TRANSFORM, transform=TRANSFORM, 
                        transparent=True, title=None, path_out=None):
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
    #fig = plt.figure(figsize=(7,5))

    fig = plt.figure(figsize=(6, 5)) #, layout="constrained")

    # devide figure in axes for colorbars and plot
    gs = GridSpec(3, 4, figure=fig, width_ratios=[0.05, 0.1, 0.8, 0.05], height_ratios=[0.1, 0.8, 0.1])
    ax_cbar_msg = fig.add_subplot(gs[1, 0])
    ax_plot = fig.add_subplot(gs[:, 2], projection=projection)
    ax_cbar_mwcch = fig.add_subplot(gs[1, -1])

    # draw filled orography if clear sky threshold is given
    if draw_oro:
        draw_orography_filled(ax_plot)
    
    # draw map
    draw_map(ax_plot, mode="light", extent=domain, cities=False)

    # draw grid    
    draw_grid(ax_plot)

    # plot msg channel
    plot_msg_data(ax_plot, msg_lons, msg_lats, 
                  msg_mask_clouds(msg_data, channelname, clear_sky_thresh) if clear_sky_thresh else msg_data, 
                  cmap=cmap, vmin=vmin, vmax=vmax, alpha=alpha, transform=transform)
    
    # draw MSG colorbar
    draw_msg_colorbar(fig, ax_cbar_msg, channelname, cmap=cmap, vmin=vmin, vmax=vmax,
                      orientation='vertical', tick_position='left')

    # plot hail probability if not None
    if mwcc_poh is not None and mwcc_lons is not None and mwcc_lats is not None:
        # plot mwcc-h probability of hail
        plot_mwcch(ax_plot, mwcc_lons, mwcc_lats, mwcc_poh, projection=projection)

    # draw MWCC-H colorbar
    draw_mwcch_colorbar(fig, ax_cbar_mwcch, orientation='vertical')
    
    # set title
    if title is not None:
         ax_plot.set_title(title, fontsize=LABELSIZE)
    
    # save to file
    if path_out is not None:
        plt.savefig(path_out, bbox_inches='tight', transparent=transparent)
        plt.close()
    else:
        plt.show()
        plt.close()

    
# %%
