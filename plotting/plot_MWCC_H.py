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
from plotting.mpl_style import LABELSIZE, TICKSIZE, TRANSFORM, CMAP_MSG_GREY
import plotting.plot_orography_and_map as map_plt
import plotting.plot_MSG as msg_plt
import readers.read_processed_MWCC_H as mwcch


# %%
def get_mwcch_color_levels(alpha=1.0, with_zero=False):

    levels = [0] if with_zero else []
    colors = [mpl.colors.to_rgba(mpl.colors.to_rgb('#F5F5F5'), alpha=alpha)] if with_zero else []

    # define levels for contour plot and ...
    levels.extend([.1, .15, .2, .25, .3, .36, .4, .5, .6, .7, .8, .9, 1])
    # colors for colobar
    colors.extend([
                    # hail potential colors
                    mpl.colors.to_rgba(mpl.colors.to_rgb('#E3E3E3'), alpha=alpha),
                    mpl.colors.to_rgba(mpl.colors.to_rgb('#C4C4C4'), alpha=alpha),
                    mpl.colors.to_rgba(mpl.colors.to_rgb('#B0B0B0'), alpha=alpha),
                    mpl.colors.to_rgba(mpl.colors.to_rgb('#9E9E9E'), alpha=alpha),
                    mpl.colors.to_rgba(mpl.colors.to_rgb('#858585'), alpha=alpha),
                    # hail colors
                    mpl.colors.to_rgba(mpl.colors.to_rgb('#98F5FF'), alpha=1.0),
                    mpl.colors.to_rgba(mpl.colors.to_rgb('#00EEEE'), alpha=1.0),
                    mpl.colors.to_rgba(mpl.colors.to_rgb('#008B8B'), alpha=1.0),
                    mpl.colors.to_rgba(mpl.colors.to_rgb('#000080'), alpha=1.0),
                    mpl.colors.to_rgba(mpl.colors.to_rgb('#00FF00'), alpha=1.0),
                    mpl.colors.to_rgba(mpl.colors.to_rgb('#FFFF00'), alpha=1.0),
                    mpl.colors.to_rgba(mpl.colors.to_rgb('#FF0000'), alpha=1.0),
                    ])

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
def plot_mwcch(ax, mwcc_lons, mwcc_lats, mwcc_poh, alpha=1.0, projection=TRANSFORM):
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

    levels, colors = get_mwcch_color_levels(alpha=alpha)
    # mask nan values and plot hail probability contours
    z = np.ma.masked_invalid(mwcc_poh)
    ax.tricontour(mwcc_lons, mwcc_lats, z, levels=levels, linewidths=0.5, colors='k', projection=projection, vmin=0, vmax=1)
    ax.tricontourf(mwcc_lons, mwcc_lats, z, levels=levels, colors=colors, projection=projection, vmin=0, vmax=1)

def plot_mwcch_hailclass(ax, mwcc_lons, mwcc_lats, mwcc_hail_class, alpha=1.0, projection=TRANSFORM):
    """ plot the hail classes of MWCC-H

    Parameters
    ----------
    ax : cartopy axis
        current axis on which to plot
    mwcc_lons : 1d-array {float}
        longitude values of each pixel
    mwcc_lats : 1d-array {float}
        latitude values of each pixel
    mwcc_hail_class : 1d-array {str}
        hail class for each pixel
    projection : cartopy projection, optional
        projection to display data in, by default ccrs.PlateCarree()
    cbar_loc : str, optional
        location of colorbar on axis, by default 'right'
    """
    hail_classes = mwcch.get_hail_class()
    levels, colors = get_mwcch_hail_class_color_levels(alpha=alpha)
    # mask nan values and plot hail probability contours
    z = np.ma.masked_invalid(mwcc_hail_class)
    ax.tricontour(mwcc_lons, mwcc_lats, z, levels=levels, linewidths=0.5, colors='k', projection=projection, vmin=0, vmax=1)
    ax.tricontourf(mwcc_lons, mwcc_lats, z, levels=levels, colors=colors, projection=projection, vmin=0, vmax=1)

def plot_mwcch_over_map(mwcc_lons, mwcc_lats, mwcc_poh, domain=domain_expats, 
                        mark_points=None, draw_subdomains=None, 
                        projection=TRANSFORM, transform=TRANSFORM, 
                        transparent=True, title=None, path_out=None):
    """ plot probability of hail contour over MSG radiances

    Parameters
    ----------
   
    """
    # create figure mit cartopy axis of certain projection
    #fig = plt.figure(figsize=(7,5))

    fig = plt.figure(figsize=(6, 5)) #, layout="constrained")

    # devide figure in axes for colorbars and plot
    gs = GridSpec(3, 2, figure=fig, width_ratios=[0.95, 0.05], height_ratios=[0.1, 0.8, 0.1])
    ax_plot = fig.add_subplot(gs[:, 0], projection=projection)
    ax_cbar = fig.add_subplot(gs[1, 1])
    
    # draw map
    map_plt.draw_map(ax_plot, mode="dark", extent=domain, cities=False)

    # draw grid    
    map_plt.draw_grid(ax_plot)

    # plot hail probability if not None
    plot_mwcch(ax_plot, mwcc_lons, mwcc_lats, mwcc_poh, projection=projection)

    # draw MWCC-H colorbar
    draw_mwcch_colorbar(fig, ax_cbar, orientation='vertical')

    # if points are given mark as crosses
    if isinstance(mark_points, list):
        for point in mark_points:
            map_plt.mark_point(ax_plot, point[0], point[1], color=point[2], marker=point[3])

    # if subdomains are given draw edges
    if isinstance(draw_subdomains, list):
        for subdom in draw_subdomains:
            map_plt.draw_subdomain(ax_plot, subdom[:4], subdom[4], subdom[5])
    
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

def plot_mwcch_over_MSG(msg_lons, msg_lats, msg_data, channelname, mwcc_lons=None, mwcc_lats=None, mwcc_poh=None, 
                        vmin=None, vmax=None, alpha_mwcch=1.0, alpha_msg=1.0, clear_sky_thresh=None, draw_oro=False,
                        mark_points=None, draw_subdomains=None,
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
        map_plt.draw_orography_filled(ax_plot)
    
    # draw map
    map_plt.draw_map(ax_plot, mode="light", extent=domain, cities=False)

    # draw grid    
    map_plt.draw_grid(ax_plot)

    # set colormap according to channel
    if "-" in channelname:
        cmap = msg_plt.create_WV_IR_diff_colormap(vmin, 0, vmax)
    else:
        cmap = CMAP_MSG_GREY

    # plot msg channel
    msg_plt.plot_msg_data(ax_plot, msg_lons, msg_lats, 
                  msg_plt.msg_mask_clouds(msg_data, channelname, clear_sky_thresh) if clear_sky_thresh else msg_data, 
                  cmap=cmap, vmin=vmin, vmax=vmax, alpha=alpha_msg, transform=transform)
    
    # draw MSG colorbar
    msg_plt.draw_msg_colorbar(fig, ax_cbar_msg, channelname, cmap=cmap, vmin=vmin, vmax=vmax,
                      orientation='vertical', tick_position='left')

    # plot hail probability if not None
    if mwcc_poh is not None and mwcc_lons is not None and mwcc_lats is not None:
        # plot mwcc-h probability of hail
        plot_mwcch(ax_plot, mwcc_lons, mwcc_lats, mwcc_poh, alpha=alpha_mwcch, projection=projection)

    # draw MWCC-H colorbar
    draw_mwcch_colorbar(fig, ax_cbar_mwcch, orientation='vertical')

    # if points are given mark as crosses
    if isinstance(mark_points, list):
        for point in mark_points:
            map_plt.mark_point(ax_plot, point[0], point[1], color=point[2], marker=point[3])

    # if subdomains are given draw edges
    if isinstance(draw_subdomains, list):
        for subdom in draw_subdomains:
            map_plt.draw_subdomain(ax_plot, subdom[:4], subdom[4], subdom[5])
    
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
