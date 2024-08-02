## using conda environment "my_satpy_env"

# %%
# import packages
import numpy as np
import matplotlib as mpl
import cartopy.feature as cfeature           # import features
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import sys

# read in own methods
sys.path.append('..')
from readers.read_orography import read_orography
from plotting.mpl_style import TRANSFORM, plot_cities_expats, TICKSIZE
from config.domain_info import domain_expats

# define style for plotting orography
ORO_GREY = mpl.cm.Greys

# define grid and map style
GRID_DARK = {"alpha": 0.5, 
             "linewidth": 0.75,
             "labels": True, 
             "labelcolor": "black", 
             "toplabels": False,
             "rightlabels": False,
             "bottomlabels": True,
             "leftlabels": True}

MAP_DARK = {"borders": True, 
            "coastlines": True, 
            "states": False, 
            "linewidth": 1, 
            "color": 'black'}

MAP_LIGHT = {"borders": True, 
            "coastlines": True, 
            "states": False, 
            "linewidth": 0.5, 
            "color": 'yellow'}

# %%
def draw_orography_filled(ax, cmap=ORO_GREY, alpha=1., transform=TRANSFORM):
    # reading orography data from raster file
    ds_or = read_orography()
    oro_levels = np.linspace(0, 1500, 20)
    oro = ax.contourf(ds_or.lons.values, 
                        ds_or.lats.values, 
                        ds_or.orography.values, 
                        transform=transform, 
                        levels=oro_levels, 
                        alpha=alpha,
                        cmap=cmap)

def draw_map(ax, extent=domain_expats, mode="dark", cities=True):
    
    if cities:
        plot_cities_expats(ax, 'black', 50)

    if mode == "dark":
        style = MAP_DARK
    elif mode == "light":
        style = MAP_LIGHT

    # Adds coastlines and borders to the current axes
    if style["borders"]:
        ax.add_feature(cfeature.BORDERS, linewidth=style["linewidth"], color=style["color"])
    if style["coastlines"]:
        ax.add_feature(cfeature.COASTLINE.with_scale('50m'), 
                       linewidth=style["linewidth"], color=style["color"])
    if style["states"]:
        ax.add_feature(cfeature.STATES, linewidth=style["linewidth"]*0.5, color=style["color"])

    # set extent
    if extent is None:
        extent = domain_expats
    ax.set_extent(extent) #[left, right, bottom ,top]

def draw_grid(ax, transform=TRANSFORM, style=GRID_DARK):

    gl = ax.gridlines(crs=transform, draw_labels=style["labels"], \
                      alpha=style["alpha"], linewidth=style["linewidth"])
    gl.top_labels = style["toplabels"]
    gl.right_labels = style["rightlabels"]
    gl.bottom_labels = style["bottomlabels"]
    gl.left_labels = style["leftlabels"]
    gl.xlabel_style = {'fontsize': TICKSIZE, 'color': style["labelcolor"]}
    gl.ylabel_style = {'fontsize': TICKSIZE, 'color': style["labelcolor"]}
    
    #gl.xformatter = LONGITUDE_FORMATTER
    #gl.yformatter = LATITUDE_FORMATTER

    #set axis thick labels
    ax.spines["top"].set_linewidth(3)
    ax.spines["right"].set_linewidth(3)
    ax.spines["bottom"].set_linewidth(3)
    ax.spines["left"].set_linewidth(3)


def mark_point(ax, lon, lat, color, marker):
    ax.scatter(lon, lat, color=color, marker=marker)


def draw_subdomain(ax, extent, color, line):
    x = [extent[0], extent[1], extent[1], extent[0], extent[0]]
    y = [extent[2], extent[2], extent[3], extent[3], extent[2]]
    ax.plot(x,y, color=color, linestyle=line)

    return None
