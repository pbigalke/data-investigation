"""
Code to read and plot the video of 1 dday radar images of rain rates
"""
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.gridspec import GridSpec
import sys

sys.path.append('..')
from config. domain_info import domain_expats
from plotting_helpers.mpl_style import LABELSIZE, TICKSIZE, TRANSFORM
from plotting_helpers.plot_orography_and_map import draw_orography_filled, draw_map, draw_grid

# %%
def draw_radar_colorbar(fig, ax, cmap=mpl.cm.BuPu_r, vmin=0., vmax=10., n_levels=15,
                        orientation='vertical', tick_position='right'):

    # create discrete colormap
    #cmaplist = [cmap(i) for i in range(cmap.N)]
    #cmap = mpl.colors.LinearSegmentedColormap.from_list('Radar color cmap', cmaplist, cmap.N)

    # define the bins and normalize
    levels = np.linspace(vmin, vmax, n_levels)
    norm = mpl.colors.BoundaryNorm(levels, cmap.N)
    cbar = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap),
                 cax=ax, orientation=orientation, shrink=0.6)

    label = r'rain rate [$kg \cdot m^{2}$]'
    cbar.set_label(label, fontsize=LABELSIZE)
    cbar.ax.tick_params(labelsize=TICKSIZE)
    ax.yaxis.set_ticks_position(tick_position)
    ax.yaxis.set_label_position(tick_position)

def plot_radar(ax, lons, lats, RR, cmap=mpl.cm.BuPu_r, vmin=0., vmax=10., n_levels=15, transform=TRANSFORM):
    # mask where no rain
    RR_masked = np.ma.masked_equal(RR, 0.)

    # define levels
    var_levels = np.linspace(vmin, vmax, n_levels)
    mesh_rr = ax.contourf(lons, 
                          lats, 
                          RR_masked, 
                          cmap=cmap, 
                          transform=transform, 
                          vmin=vmin,  
                          vmax=vmax, 
                          levels=var_levels, 
                          extend='max',
                          alpha=0.6)  
    
def plot_radar_over_map(lats, lons, RR, cmap=mpl.cm.BuPu_r, vmin=0, vmax=10, n_levels=15, 
                      domain=domain_expats, projection=TRANSFORM, transform=TRANSFORM, 
                      transparent=True, title=None, path_out=None):
    
    """
    function to plot map of radar data from DWD, in rain rate

    Args:
        data (xarray dataset): data from DWD 
    """
    fig = plt.figure(figsize=(6, 5)) #, layout="constrained")

    # devide figure in axes for colorbars and plot
    gs = GridSpec(3, 2, figure=fig, width_ratios=[0.95, 0.05], height_ratios=[0.1, 0.8, 0.1])
    ax_plot = fig.add_subplot(gs[:, 0], projection=projection)
    ax_cbar = fig.add_subplot(gs[1, 1])

    # draw orography
    draw_orography_filled(ax_plot)
    
    # draw map
    draw_map(ax_plot, extent=domain)

    # draw grid    
    draw_grid(ax_plot)

    # plot rain rate as filled contours
    plot_radar(ax_plot, lons, lats, RR, cmap=cmap, vmin=vmin, vmax=vmax, n_levels=n_levels, transform=transform)

    # draw color bar
    draw_radar_colorbar(fig, ax_cbar, cmap=cmap, vmin=vmin, vmax=vmax, n_levels=n_levels, 
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


