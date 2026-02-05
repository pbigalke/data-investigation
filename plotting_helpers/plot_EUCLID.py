## using conda environment "my_satpy_env"

# %%
# import packages
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.gridspec import GridSpec
import sys

sys.path.append('..')
from config.domain_info import domain_expats
from plotting_helpers.mpl_style import LABELSIZE, TICKSIZE, TRANSFORM, CMAP_MSG_GREY
import plotting_helpers.plot_orography_and_map as map_plt
import plotting_helpers.plot_MSG as msg_plt
import readers.read_processed_MWCC_H as mwcch


# %%
# def get_euclid_color_levels(alpha=1.0, with_zero=False):

#     levels = [0] if with_zero else []
#     colors = [mpl.colors.to_rgba(mpl.colors.to_rgb('#F5F5F5'), alpha=alpha)] if with_zero else []

#     # define levels for contour plot and ...
#     levels.extend([10, 20, 30])
#     # colors for colobar
#     cmap = mpl.cm.get_cmap('RdPu')
#     colors.extend([cmap(i) for i in np.linspace(0.1, 0.9, len(levels))])

#     return levels, colors

# # create colormap where all zero values are transparent
# def get_euclid_colormap(alpha=1.0, with_zero=False):
#     levels, colors = get_euclid_color_levels(alpha=alpha, with_zero=with_zero)
#     cmap = mpl.colors.ListedColormap(colors)
#     norm = mpl.colors.BoundaryNorm(levels, cmap.N)
#     return cmap, norm

def get_euclid_colormap(cmap_name='RdPu', vmin=10, vmax=30, ncolors=256, alpha=1.0):
    """
    Create a colormap where values below vmin are transparent.
    """
    base_cmap = plt.get_cmap(cmap_name, ncolors)
    # Convert to array and set alpha
    colors = base_cmap(np.linspace(0.3, 1, ncolors))
    colors[:, 3] = alpha  # Set alpha for all colors

    # Create new colormap with modified alpha
    cmap = mpl.colors.ListedColormap(colors)
    # Set 'under' color to fully transparent
    cmap = cmap.with_extremes(under=(0, 0, 0, 0))

    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax, clip=False)
    return cmap, norm

def draw_euclid_colorbar(fig, ax, cmap_name='RdPu', vmin=10, vmax=30, alpha=1.0, orientation='vertical'):

    cmap, norm = get_euclid_colormap(cmap_name=cmap_name, vmin=vmin, vmax=vmax, alpha=alpha)
    cbar = fig.colorbar(mpl.cm.ScalarMappable(cmap=cmap, norm=norm),
                        cax=ax, orientation=orientation,
                        spacing='uniform')
    cbar.set_label('total lightning count', fontsize=LABELSIZE)


# %%
def plot_euclid(ax, euclid_lons, euclid_lats, euclid_data, alpha=1.0, 
                cmap_name='RdPu', vmin=10, vmax=30, projection=TRANSFORM):
    """ plot the lightning counts from EUCLID

    Parameters
    ----------
    ax : cartopy axis
        current axis on which to plot
    euclid_lons : 1d-array {float}
        longitude values of the grid
    euclid_lats : 1d-array {float}
        latitude values of the grid
    euclid_data : 1d-array {float}
        lightning counts for each pixel
    projection : cartopy projection, optional
        projection to display data in, by default ccrs.PlateCarree()
    """    
    # mask nan values and plot hail probability contours
    z = np.ma.masked_invalid(euclid_data)

    # create 2d grid from lons and lats 1d-arrays
    xs, ys = np.meshgrid(euclid_lons, euclid_lats)

    # get colors for contour lines
    # levels, colors = get_euclid_color_levels(alpha=alpha)
    # # draw contours
    # ax.contour(xs, ys, z, levels=levels, linewidths=0.5, colors='k', projection=projection)
    # ax.contourf(xs, ys, z, levels=levels, colors=colors, projection=projection)

    cmap, norm = get_euclid_colormap(cmap_name=cmap_name, vmin=vmin, vmax=vmax, alpha=alpha)
    # plot data with colormap
    pc = ax.pcolormesh(xs, ys, z, cmap=cmap, norm=norm, transform=projection)

    return pc

def plot_euclid_over_map(euclid_lons, euclid_lats, euclid_data, domain=domain_expats, 
                        cmap_name='RdPu', vmin=1, vmax=20, mark_points=None, draw_subdomains=None, 
                        projection=TRANSFORM, transform=TRANSFORM, 
                        transparent=True, title=None, path_out=None):
    """ plot euclid total lightning counts as contour

    Parameters
    ----------
   euclid_lons : 1d-array {float}
        longitude values of each pixel
    euclid_lats : 1d-array {float}
        latitude values of each pixel
    euclid_data : 2d-array {float}
        total lightning counts for each pixel
    extent : list(float), optional
        [minlon, maxlon, minlat, maxlat], by default None
    projection : cartopy projection, optional
        projection to display data in, by default ccrs.PlateCarree()
    transform : cartopy transformation, optional
        transformation in which the data is given, by default ccrs.PlateCarree()
    title : string, optional
        title of figure, by default None
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

    # plot euclid lightning counts
    plot_euclid(ax_plot, euclid_lons, euclid_lats, euclid_data, projection=projection, 
                cmap_name=cmap_name, vmin=vmin, vmax=vmax)

    # draw EUCLID colorbar
    draw_euclid_colorbar(fig, ax_cbar, cmap_name=cmap_name, vmin=vmin, vmax=vmax, orientation='vertical')

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

def plot_euclid_over_MSG(msg_lons, msg_lats, msg_data, channelname, 
                        euclid_lons=None, euclid_lats=None, euclid_data=None, 
                        vmin_msg=None, vmax_msg=None, alpha_msg=1.0, clear_sky_thresh=None,
                        cmap_euclid='RdPu', vmin_euclid=1, vmax_euclid=20, alpha_euclid=1.0,
                        draw_oro=False, mark_points=None, draw_subdomains=None,
                        domain=domain_expats, projection=TRANSFORM, transform=TRANSFORM, 
                        transparent=True, title=None, path_out=None):
    """ plot euclid total lightning counts as contour

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
    ax_cbar = fig.add_subplot(gs[1, -1])

    # draw filled orography if clear sky threshold is given
    if draw_oro:
        map_plt.draw_orography_filled(ax_plot)
    
    # draw map
    map_plt.draw_map(ax_plot, mode="light", extent=domain, cities=False)

    # draw grid    
    map_plt.draw_grid(ax_plot)

    # set colormap according to channel
    if "-" in channelname:
        cmap = msg_plt.create_WV_IR_diff_colormap(vmin_msg, 0, vmax_msg)
    else:
        cmap = CMAP_MSG_GREY

    # plot msg channel
    msg_plt.plot_msg_data(ax_plot, msg_lons, msg_lats, 
                  msg_plt.msg_mask_clouds(msg_data, channelname, clear_sky_thresh) if clear_sky_thresh else msg_data, 
                  cmap=cmap, vmin=vmin_msg, vmax=vmax_msg, alpha=alpha_msg, transform=transform)

    # draw MSG colorbar
    msg_plt.draw_msg_colorbar(fig, ax_cbar_msg, channelname, cmap=cmap, vmin=vmin_msg, vmax=vmax_msg,
                      orientation='vertical', tick_position='left')

    # plot hail probability if not None
    if euclid_data is not None and euclid_lons is not None and euclid_lats is not None:
        # plot euclid data
        plot_euclid(ax_plot, euclid_lons, euclid_lats, euclid_data, alpha=alpha_euclid, projection=projection,
                    cmap_name=cmap_euclid, vmin=vmin_euclid, vmax=vmax_euclid)

    # draw EUCLID colorbar
    draw_euclid_colorbar(fig, ax_cbar, cmap_name=cmap_euclid, vmin=vmin_euclid, vmax=vmax_euclid, orientation='vertical')

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
