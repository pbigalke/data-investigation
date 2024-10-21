# %%
import glob
import xarray as xr
import numpy as np
import datetime
import matplotlib.pyplot as plt
import matplotlib as mpl
import os
import sys
sys.path.append("..")
import readers.read_processed_MWCC_H as mwcch_read
import readers.read_MSG as msg_read
import plotting.plot_MWCC_H as mwcch_plt

datapath = mwcch_read.MWCCH_MSGGRID_PATH
plotpath = "/net/merisi/pbigalke/plots/data_investigation/MWCC-H_hail_occurrence"

def load_counter_file(counter_filename):
  if os.path.exists(counter_filename):
    print("thingy is here: ", counter_filename)
    with xr.load_dataset(counter_filename) as counter:
      return counter
  return None

# %%
# plot hail class occurrence per area 
def occurrence_per_area_fraction(years):
  # define plot path and file name of specific counter file
  counter_file = f"{datapath}/statistics/overpasses_per_year_hailclass_area.nc"
  overpass_hailclass_area = load_counter_file(counter_file)

  out = f"{plotpath}/area_covered_by_overpasses_{years[0]}-{years[-1]}.png"
  barplot_occurrences_per_area_fraction(overpass_hailclass_area, year_start=years[0], year_end=years[-1],
                                        output_name=out, figsize=(8, 5), fraction=False, log=False)
  out_log = f"{plotpath}/area_covered_by_overpasses_{years[0]}-{years[-1]}_log.png"
  barplot_occurrences_per_area_fraction(overpass_hailclass_area, year_start=years[0], year_end=years[-1],
                                        output_name=out_log, figsize=(8, 5),
                                        fraction=False, log=True)
  out_frac = f"{plotpath}/area_covered_by_overpasses_{years[0]}-{years[-1]}_frac.png"
  barplot_occurrences_per_area_fraction(overpass_hailclass_area, year_start=years[0], year_end=years[-1],
                                        output_name=out_frac, figsize=(8, 5),
                                        fraction=True, log=False)
  out_frac_log = f"{plotpath}/area_covered_by_overpasses_{years[0]}-{years[-1]}_frac_log.png"
  barplot_occurrences_per_area_fraction(overpass_hailclass_area, year_start=years[0], year_end=years[-1],
                                        output_name=out_frac_log, figsize=(8, 5),
                                        fraction=True, log=True)

def barplot_occurrences_per_area_fraction(overpass_hailclass_area, year_start=1999, year_end=2023,
                                          output_name=None, figsize=(10, 8),
                                          fraction=False, log=False):
  
  f, ax = plt.subplots(1)
  f.set_figheight(figsize[1])
  f.set_figwidth(figsize[0])
  ax.set_title("distribution of covered area fraction")

  # select the data for the given year range and sum over all years
  overpass_hailclass_area = overpass_hailclass_area.sel(year=slice(year_start, year_end)).sum(dim="year")

  # get total number of overpasses in dataset
  N_total = overpass_hailclass_area.N_overpasses.sum().values

  # get hail class names
  hail_class_names = mwcch_read.get_hail_classes(type="name")

  # define bottom of barplots
  bottom = np.zeros(overpass_hailclass_area.area_perc.shape)

  # loop over hail classes and fill in barplots
  for h in overpass_hailclass_area.hail_class.values:

    # get counts only for this hail_class
    area_counts = overpass_hailclass_area.N_overpasses.sel(hail_class=h).values

    # get color of hail_class
    color = mwcch_plt.hail_class_colors_list[int(h)]

    # bar plot of number of overpasses per area fraction
    y = area_counts / N_total * 100 if fraction else area_counts
    x_center = overpass_hailclass_area.area_perc.values
    ax.bar(x_center, y, -0.8, color=color, align="center", bottom=bottom, label=hail_class_names[h])

    # set bottom for next hail_class
    bottom += y

  # format x axes
  ax.set_xlim(x_center[0]-0.5, x_center[-1] + 0.5)
  ax.set_xlabel("area covered by overpass [%]")

  # mark area for different crop sizes
  msglon, msglat = msg_read.get_lon_lat()
  N_pix = len(msglon) * len(msglat)
  for crop in [128, 200]:
    area_crop = crop * crop / N_pix * 100
    # draw vertical line
    ax.axvline(x=area_crop, color="k", linestyle="--", linewidth=0.5)
    # convert data coordinates to display coordinates
    display_coords = ax.transData.transform((area_crop, 0.5))
    # convert display coordinates to axes coordinates
    axes_coords = ax.transAxes.inverted().transform(display_coords)
    # add text next to line using axes coordinates
    ax.text(axes_coords[0], 0.9, f"{crop}x{crop}", fontsize=8, 
            verticalalignment='center', transform=ax.transAxes)
    
  # format y axes
  ax.set_ylabel("fraction of all overpasses" if fraction else "number of overpasses")
  if log:
    ax.set_yscale('log')
  ax.grid(True)

  plt.tight_layout()

  if output_name is not None:
    plt.savefig(output_name, bbox_inches='tight')
    plt.close()
  else:
    plt.show()
    plt.close()


# %%
# plot the percentage of hail classes per area threshold and year
def occurrence_per_year_and_coveredarea():
  # define plot path and file name of specific counter file
  counter_file = f"{datapath}/statistics/overpasses_per_year_hailclass_area.nc"
  overpass_year_hailclass_area = load_counter_file(counter_file)

  year_start = [1999, 2006]
  for y in year_start:
    out = f"{plotpath}/hail_occurrence_per_area_thresh_and_year_{y}onwards.png"
    hailclass_percentage_per_area_thresh_and_year(overpass_year_hailclass_area, year_start=y, output_name=out)

def hailclass_percentage_per_area_thresh_and_year(overpass_year_hailclass_area, year_start=2006, output_name=None):
  
  # get hail classes  
  hail_classes = overpass_year_hailclass_area.hail_class.values 

  # filter for year_start
  overpass_area_year_hail = overpass_year_hailclass_area.sel(year=slice(year_start, None))

  # regroup data by larger area bins
  # Step 1: Define the new bins
  new_area_bins = np.arange(0, 110, 10)
  # Step 2: Group the data by the new bins
  grouped = overpass_area_year_hail.groupby_bins('area_perc', new_area_bins, right=True)
  # Step 3: Aggregate the counts within each new bin
  aggregated_counts = grouped.sum()
  # get total number of overpasses per year and area_bin
  total_overpasses = aggregated_counts.sum(dim=["hail_class"]).N_overpasses.values

  # get axis arrays
  years = overpass_area_year_hail.year.values

  # create figure with gridspec
  fig = plt.figure(figsize=(4, 2*(len(hail_classes)+1)))
  gs = mpl.gridspec.GridSpec(len(hail_classes)+1, 2, width_ratios=[20, 1], 
                             hspace=0.3, wspace=0)

  # first plot total number of overpasses per area bin and year
  ax = fig.add_subplot(gs[0, 0])
  c = ax.imshow(total_overpasses, cmap="inferno", origin="lower")
  cbar_ax = fig.add_subplot(gs[0, 1])
  fig.colorbar(c, cax=cbar_ax, label="# overpasses") #, fraction=0.046, pad=0.04
  # add hail class text in the bottom left corner
  ax.text(0.01, 0.01, "total number of overpasses", 
          transform=ax.transAxes, fontsize=10, verticalalignment='bottom',
          color="white")

  # loop over hail classes
  for hail in hail_classes:
    ax = fig.add_subplot(gs[int(hail)+1, 0])
    # ax.set_title(f"{mwcch_read.get_hail_classes(type='name')[int(hail)]}")

    # get number of overpasses per area bin and year
    n_hail = aggregated_counts.where(overpass_year_hailclass_area.hail_class == hail, drop=True)
    perc_hail = n_hail.N_overpasses.values[:, :, 0] / total_overpasses * 100
    # Replace NaN values with zero
    perc_hail[np.isnan(perc_hail)] = 0

    # plot percentage of hail class per area bin and year
    c = ax.imshow(perc_hail, cmap="inferno", origin="lower")#, 
                  # vmin=0, vmax=vmax)
    cbar_ax = fig.add_subplot(gs[int(hail)+1, 1])
    fig.colorbar(c, cax=cbar_ax, label="Occurrence [%]")

    # add hail class text in the bottom left corner
    ax.text(0.01, 0.01, mwcch_read.get_hail_classes(type='name')[int(hail)], 
            transform=ax.transAxes, fontsize=10, verticalalignment='bottom',
            color="white")

  # format axes
  for ax in fig.get_axes():
    if ax.get_subplotspec().is_first_col():
      ax.set_yticks(np.arange(0, len(new_area_bins))-0.5, labels=new_area_bins, fontsize=8)
      ax.set_ylim(-0.5, len(new_area_bins)-1.5)
      ax.set_ylabel("area [%]")
      ax.set_xticks(np.arange(0, len(years), 1)-0.5, 
                    labels=years, rotation=-45, ha='left', fontsize=8)
      ax.set_xlim(-0.5, len(years)-0.5)
      if not ax.get_subplotspec().is_last_row():
        ax.set_xticklabels([]) 
      else:
        ax.set_xlabel("years")
        # Turn off every second x-tick label
        labels = ax.get_xticklabels()
        for i, label in enumerate(labels):
            if i % 2 != 0:
                labels[i] = ''
        ax.set_xticklabels(labels)

  # plt.tight_layout()

  if output_name is not None:
    plt.savefig(output_name, bbox_inches='tight')
    plt.close()
  else:
    plt.show()
    plt.close()


# %%
def hailclass_development_per_area_thresholds():
  # define plot path and file name of specific counter file
  counter_file = f"{datapath}/statistics/overpasses_per_year_hailclass_area.nc"
  overpass_year_hailclass_area = load_counter_file(counter_file)

  # different thresholds
  area_thresh = [0, 10, 20, 30, 40, 50, 60]
  year_start = [1999, 2006]
  for y in year_start:
    out = f"{plotpath}/hail_class_development_per_areathresh_{y}onwards.png"
    plot_hailclass_development_per_areathresh(overpass_year_hailclass_area, area_thresh, year_start=y, 
                                              output_name=out)

def plot_hailclass_development_per_areathresh(overpass_area_year_hail, area_thresh, year_start=2006,
                                              output_name=None, figsize=(10, 15)):
  
  # number of area thresholds
  N_thresh = len(area_thresh)
  colors = plt.cm.viridis(np.linspace(0, 1, N_thresh))

  # filter for year_start
  overpass_area_year_hail = overpass_area_year_hail.sel(year=slice(year_start, None))

  # get hail class names
  hail_class_names = mwcch_read.get_hail_classes(type="name")

  # create figure 
  f, axes = plt.subplots(len(hail_class_names))
  f.set_figheight(figsize[1])
  f.set_figwidth(figsize[0])

  # loop over area thresholds
  for t, thresh in enumerate(area_thresh):

    # select only overpasses with certain area threshold and sum over all areas
    area_filtered_data = \
      overpass_area_year_hail.where(overpass_area_year_hail['area_perc'] >= thresh, drop=True)

    # get number of overpasses per year and hail_class
    yearly_hail_counts = area_filtered_data.N_overpasses.sum(dim=["area_perc"])

    # get total number of overpasses per year
    N_total = yearly_hail_counts.sum("hail_class").values

    # loop over hail class
    for hail in yearly_hail_counts.hail_class.values:
      # get axis for this hail class
      ax = axes[int(hail)]

      # get percentage of overpasses containing this hail class
      n_class = yearly_hail_counts.sel(hail_class=hail).values / N_total * 100
      
      # draw development over the years for this hail class
      ax.plot(yearly_hail_counts.year.values, n_class, 
              color=colors[t], #mwcch_plt.hail_class_colors_list[int(hail)], 
              #alpha=1-t*(0.6 / N_thresh), linestyle="-", 
              label=f">={thresh}%")
      
      if t == 0:
        # add hail class text in the bottom left corner
        ax.text(0.2, 0.9, mwcch_read.get_hail_classes(type='name')[int(hail)], 
            transform=ax.transAxes, fontsize=10, verticalalignment='bottom',
            color="k")
  
  # format x axes
  for ax in axes:
    if ax == axes[0]:
      ax.legend(loc=0, frameon=True)
    if ax == axes[-1]:
      ax.set_xlabel("year")
    ax.set_xticks(yearly_hail_counts.year.values[1::2])
    ax.set_xlim(yearly_hail_counts.year.values[0]-0.5, yearly_hail_counts.year.values[-1]+0.5)
    if ax != axes[-1]:
      ax.set_xticklabels([])
    ax.set_ylabel("occurrence [%]")
    ax.grid(True)

  plt.tight_layout()

  if output_name is not None:
    plt.savefig(output_name, bbox_inches='tight')
    plt.close()
  else:
    plt.show()
    plt.close()
    

# %%
# plot the distribution of hail classes per area thresholds
def hailclass_distribution_per_area_thresholds(years):
  # define plot path and file name of specific counter file
  counter_file = f"{datapath}/statistics/overpasses_per_year_hailclass_area.nc"
  overpass_hailclass_area = load_counter_file(counter_file)

  # different thresholds
  area_thresh = [0, 10, 20, 30, 40, 50, 60]
  out = f"{plotpath}/hail_class_distribution_per_areathresh_{years[0]}-{years[-1]}_hailclasses_separated.png"
  plot_hailclass_distribution_per_areathresh(overpass_hailclass_area, area_thresh=area_thresh, 
                                             year_start=years[0], year_end=years[-1], output_name=out)

def plot_hailclass_distribution_per_areathresh(overpass_hailclass_area, area_thresh, 
                                               year_start=2006, year_end=2023, output_name=None, 
                                               figsize=(15, 5)):
  
  f, axes = plt.subplots(1, 2, layout='constrained', width_ratios=[2, 3])
  f.set_figheight(figsize[1])
  f.set_figwidth(figsize[0])
  # ax1.set_title("distribution of hail classes per area threshold")

  # select the data for the given year range and sum over all years
  overpass_hailclass_area = overpass_hailclass_area.sel(year=slice(year_start, year_end)).sum(dim="year")

  # get hail class names
  hail_class_names = mwcch_read.get_hail_classes(type="name")

  # devide into non-hail and hail classes
  hail_group_idx = [np.array([0, 1]).astype(int), np.arange(2, len(hail_class_names)).astype(int)]

  # get step between bars and bar width
  step = 0.8 / len(area_thresh)
  width = 0.75 / len(area_thresh)

  # loop over area thresholds
  for t, thresh in enumerate(area_thresh):

    # select only overpasses with certain area threshold and sum over all areas
    area_filtered_data = overpass_hailclass_area.where(overpass_hailclass_area['area_perc'] >= thresh, drop=True)

    # get number of overpasses per hail_class over all areas
    hail_counts = area_filtered_data.N_overpasses.sum(dim=["area_perc"])

    # get total number of overpasses in dataset
    N_total = hail_counts.sum().values
      
    # get total number and percentage of overpasses containing this hail class
    n_class = hail_counts.values / N_total * 100
    
    for g, hail_group in enumerate(hail_group_idx):
      # plot the NON_HAIL classes
      ax1 = axes[g]
      # set x positions for bars
      x_positions = np.arange(0, len(hail_group), 1) + t * step
      # get colors for these hail classes
      colors = [mwcch_plt.hail_class_colors_list[i] for i in hail_group]
      # plot bar for this class
      ax1.bar(x_positions, n_class[hail_group], width, 
              color=colors, align="center")
      
  # set x ticks for area thresholds
  for g, hail_group in enumerate(hail_group_idx):
    # select axis
    ax1 = axes[g]

    # Add borders around the plot
    for spine in ax1.spines.values():
        spine.set_visible(True)

    # first ticks for the area thresholds
    x_thresh = np.arange(0, len(hail_group), 1)
    thresh_ticks = np.sort(np.concatenate([x_thresh + step * t for t in range(len(area_thresh))]))
    thresh_tick_labels = [f"{l}" for l in np.tile(area_thresh, len(hail_group)).flatten()]
    ax1.set_xticks(thresh_ticks, labels=thresh_tick_labels) #, rotation=45, ha='right')
    ax1.set_xlabel("area threshold [%]")

    # second ticks for the class names
    sec = ax1.secondary_xaxis(location='top')
    x_class = np.arange(0, len(hail_group), 1) + step * (len(area_thresh) / 2. - 0.5)
    class_names = [hail_class_names[i] for i in hail_group]
    sec.set_xticks(x_class, labels=class_names)

    # format the rest of the axes
    ax1.set_xlim(-0.15, len(hail_group))
    ax1.set_ylabel("occurrence [%]")
    # set y axis on the right for second plot
    if g == 1:
      ax1.yaxis.tick_right()
      ax1.yaxis.set_label_position('right')
    ax1.grid(axis='x')

  # plt.tight_layout()

  if output_name is not None:
    plt.savefig(output_name, bbox_inches='tight')
    plt.close()
  else:
    plt.show()
    plt.close()


# %%
def hailclass_distribution_and_development_for_area_threshold():
  # define plot path and file name of specific counter file
  counter_file = f"{datapath}/statistics/overpasses_per_year_hailclass_area.nc"
  overpass_year_hailclass_area = load_counter_file(counter_file)

  starting_year = [2006] 
  for y in starting_year:
    # loop over different thresholds
    for t in [0, 10, 20, 30, 40, 50, 60]:  #]:

      out = f"{plotpath}/hail_class_distribution_development_areathresh{t}_{y}onwards.png"
      plot_hailclass_distribution_and_development(overpass_year_hailclass_area, 
                                                  area_threshold=t, output_name=out)

      out_only_hail = f"{plotpath}/hail_class_distribution_development_areathresh{t}_{y}onwards_onlyhail.png"
      plot_hailclass_distribution_and_development(overpass_year_hailclass_area, area_threshold=t, year_start=y,
                                                  output_name=out_only_hail, only_hail=True)

def plot_hailclass_distribution_and_development(overpass_year_hailclass_area, area_threshold=0, year_start=2006, 
                                                output_name=None, figsize=(15, 5), fraction=False, only_hail=False):
  
  f, (ax1, ax2) = plt.subplots(1, 2, width_ratios=[1,2])
  f.set_figheight(figsize[1])
  f.set_figwidth(figsize[0])
  ax1.set_title("distribution of hail classes")
  ax2.set_title("hail classes over the years")

  # select only overpasses with certain area threshold
  area_filtered_data = overpass_year_hailclass_area.where(overpass_year_hailclass_area['area_perc'] >= area_threshold, drop=True)

  # sum over all areas
  yearly_hail_counts = area_filtered_data.N_overpasses.sum(dim=["area_perc"])

  # filter for year_start
  yearly_hail_counts = yearly_hail_counts.sel(year=slice(year_start, None))

  # get total number of overpasses in dataset
  N_total = yearly_hail_counts.sum().values

  # get total number of overpasses per year
  N_total_yearly = yearly_hail_counts.sum(dim=["hail_class"]).values

  # get hail class names
  hail_class_names = mwcch_read.get_hail_classes(type="name")

  # loop over hail class
  for h in yearly_hail_counts.hail_class.values:
    
    # get total number and percentage of overpasses containing this hail class
    n_class = yearly_hail_counts.sum(dim=["year"]).sel(hail_class=h).values
    perc_class = n_class / N_total * 100 
    if fraction:
      n_class = perc_class
    
    # plot bar for this class
    ax1.bar(h, n_class, -0.8, 
            color=mwcch_plt.hail_class_colors_list[int(h)], 
            align="center")

    # add percentage above max poh bars
    position = 1 if n_class == 0 else n_class
    ax1.text(h, position, f'{perc_class:.2f}', fontsize=12, 
              horizontalalignment='center', verticalalignment='bottom')

    if only_hail and h <= 1:
      continue

    # draw development over the years for this hail class
    n_class_yearly = yearly_hail_counts.sel(hail_class=h)
    perc_class_yearly = n_class_yearly.values / N_total_yearly * 100 
    ax2.plot(n_class_yearly.year.values, perc_class_yearly, 
            color=mwcch_plt.hail_class_colors_list[int(h)], 
            linestyle="-", label=hail_class_names[int(h)])

  # format x axes
  x_center = np.arange(0, len(yearly_hail_counts.hail_class), 1)
  ax1.set_xticks(x_center, labels=hail_class_names, rotation=45, ha='right')
  ax1.set_xlim(x_center[0]-0.5, x_center[-1] + 0.5)
  ax1.set_ylabel("fraction of all files" if fraction else "number of files")
  ax1.grid(False)
  #
  ax2.set_xlim(yearly_hail_counts.year.values[0], yearly_hail_counts.year.values[-1])
  ax2.set_xlabel("year")
  ax2.set_xticks(yearly_hail_counts.year.values[1::2])
  ax2.legend(loc=0, frameon=True)
  ax2.grid(True)

  plt.tight_layout()

  if output_name is not None:
    plt.savefig(output_name, bbox_inches='tight')
    plt.close()
  else:
    plt.show()
    plt.close()


# %%
def hailclass_overpass_per_satellite_year_and_area_threshold():
  # define plot path and file name of specific counter file
  counter_file = f"{datapath}/statistics/overpasses_per_year_hour_hailclass_covered_area_sat.nc"
  overpass_satellite_area = load_counter_file(counter_file)
  
  hail_classes = mwcch_read.get_hail_classes(type="name") + ["all"]
  starting_year = [1999, 2006]
  for y in starting_year:
    for h, hail in enumerate(hail_classes):

      out = f"{plotpath}/overpasses_per_satellite_and_areathresh_{y}onwards_{hail}.png"
      satellite_overpasses_per_area_thresh_and_year(overpass_satellite_area, year_start=y, 
                                                    hail_class=h, hail_class_name=hail,
                                                    output_name=out)

def satellite_overpasses_per_area_thresh_and_year(overpass_hailclass_hour_area_sat, year_start=2006, 
                                                  hail_class=None, hail_class_name="all", output_name=None):
  
  # get satellites  
  sats = overpass_hailclass_hour_area_sat.sat.values

  # filter for year_start
  overpass_hailclass_hour_area_sat = overpass_hailclass_hour_area_sat.sel(year=slice(year_start, None))

  # sum over all hour
  overpass_year_area_sat = overpass_hailclass_hour_area_sat.sum(dim="hour")

  # select given hail class or sum over all hail classes
  if hail_class_name != "all":
    overpass_year_area_sat = overpass_year_area_sat.where(overpass_year_area_sat.hail_class == hail_class, drop=True)
  overpass_year_area_sat = overpass_year_area_sat.sum(dim="hail_class")

  # regroup data by larger area bins
  # Step 1: Define the new bins
  new_area_bins = np.arange(0, 110, 10)
  # Step 2: Group the data by the new bins
  grouped = overpass_year_area_sat.groupby_bins('area_perc', new_area_bins, right=True)
  # Step 3: Aggregate the counts within each new bin
  aggregated_counts = grouped.sum()

  # get axis arrays
  years = overpass_year_area_sat.year.values

  # create figure with gridspec
  fig = plt.figure(figsize=(15, 8))
  fig.suptitle(f"hail class: {hail_class_name}")
  n_rows = 5
  n_cols = 3
  gs = mpl.gridspec.GridSpec(n_rows, n_cols*2, width_ratios=[20, 1, 20, 1, 20, 1], 
                             hspace=0.05, wspace=0.03)

  # loop over satellites
  for s, sat in enumerate(sats):
    ax = fig.add_subplot(gs[s%5, 2*np.floor(s/5.).astype(int)])

    # get number of overpasses per area bin and year
    n_sat = aggregated_counts.where(aggregated_counts.sat == sat, drop=True).N_overpasses.values

    # plot percentage of hail class per area bin and year
    c = ax.imshow(n_sat, cmap="inferno", origin="lower")#, 
                  # vmin=0, vmax=vmax)
    cbar_ax = fig.add_subplot(gs[s%5, 2*np.floor(s/5.).astype(int)+1])
    fig.colorbar(c, cax=cbar_ax, label="# overpasses")

    # add sat text in the upper middle
    ax.text(0.5, 0.95, f"{sat}", transform=ax.transAxes, 
            fontsize=10, verticalalignment='top', horizontalalignment='center',
            color="white")

  # format axes
  for ax in fig.get_axes():
    subplot_spec = ax.get_subplotspec()
    nrows, ncols, row, col = subplot_spec.get_geometry()
    
    if col % 2 == 0:  # Check if the column index is even
      ax.set_yticks(np.arange(0, len(new_area_bins))-0.5, labels=new_area_bins, fontsize=8)
      ax.set_ylim(-0.5, len(new_area_bins)-1.5)
      ax.set_ylabel("area [%]")
      ax.set_xticks(np.arange(0, len(years), 1)-0.5, 
                    labels=years, rotation=-45, ha='left', fontsize=8)
      ax.set_xlim(-0.5, len(years)-0.5)
    if ax.get_subplotspec().is_last_row():
      ax.set_xlabel("years")
      # Turn off every second x-tick label
      labels = ax.get_xticklabels()
      for i, label in enumerate(labels):
          if i % 2 != 0:
              labels[i] = ''
      ax.set_xticklabels(labels)
    else:
      ax.set_xticklabels([]) 

  # plt.tight_layout()

  if output_name is not None:
    plt.savefig(output_name, bbox_inches='tight')
    plt.close()
  else:
    plt.show()
    plt.close()



# %%
# plot the distribution of hail classes per min_pixel
def hailclass_distribution_per_min_pixel_for_areathresh():
  # define plot path and file name of specific counter file
  counter_file = f"{datapath}/statistics/overpasses_per_year_hailclass_minpix_and_covered_area.nc"
  overpass_hailclass_minpix_area = load_counter_file(counter_file)

  area_thresholds = [0, 10, 20, 30, 40, 50, 60]
  starting_year = [2006]
  for y in starting_year:
    out = f"{plotpath}/hail_class_distribution_per_minpixe_{y}onwards.png"
    plot_hailclass_distribution_per_min_pixel_for_areathresh(overpass_hailclass_minpix_area, area_thresholds, 
                                               year_start=y, output_name=out)
    
    out = f"{plotpath}/number_of_hailclass_files_per_minpixel_and_areathresh_{y}onwards.png"
    plot_files_per_min_pixel_and_areathresh_for_hailclasses(overpass_hailclass_minpix_area, area_thresholds, 
                                                            year_start=2006, output_name=out)

def plot_hailclass_distribution_per_min_pixel_for_areathresh(overpass_hailclass_area, area_thresholds, 
                                                year_start=2006, output_name=None):

  # filter for year_start and sum over all years
  overpass_hailclass_area = overpass_hailclass_area.sel(year=slice(year_start, None)).sum(dim="year")

  # create figure with gridspec
  n_rows = np.ceil(len(area_thresholds) / 2.).astype(int)
  n_cols = 2
  fig = plt.figure(figsize=(5*n_cols, 1.5*n_rows))
  gs = mpl.gridspec.GridSpec(n_rows, 2*n_cols, width_ratios=[20, 1, 20, 1], 
                             hspace=0.3, wspace=0.3)
  
  # loop over area thresholds
  for t, thresh in enumerate(area_thresholds):

    # get axis for this area threshold
    ax = fig.add_subplot(gs[int(t/2), 2*(t%2)])
    ax.set_title(f"coverage >={thresh}%", fontsize=10)

    # select only overpasses with certain area threshold
    area_filtered_data = overpass_hailclass_area.where(overpass_hailclass_area['area_perc'] >= thresh, drop=True)
    # sum over all areas
    hail_class_counts = area_filtered_data.N_overpasses.sum(dim=["area_perc"])

    # get only hail classes
    hail_counts = hail_class_counts.where(hail_class_counts.hail_class > 1, drop=True)

    # first entry as reference (min_pixel=1)
    ref_counts = hail_counts.sel(min_pixel=1).values

    # plot percentage of hail class per area bin and year
    c = ax.imshow(hail_counts.values-ref_counts[:, np.newaxis], cmap="inferno", origin="lower") #, norm="log")#, 
                  # vmin=0, vmax=vmax)

    # plot colorbar
    cbar_ax = fig.add_subplot(gs[int(t/2), 2*(t%2)+1])
    fig.colorbar(c, cax=cbar_ax, label="# files lost")

  # get hail classes  
  hail_classes = hail_counts.hail_class.values
  hail_class_names = mwcch_read.convert_hail_class(hail_classes, to="name")

  # get min pixel values
  min_pix = overpass_hailclass_area.min_pixel.values
    
  # format axes
  for r in np.arange(n_rows):
    for c in np.arange(0, 2*n_cols, 2):
      try:
        ax = fig.get_axes()[r*2*n_cols + c]
        ax.set_xticks(np.arange(0, len(min_pix)), labels=min_pix, fontsize=8)
        ax.set_xlim(-0.5, len(min_pix)-0.5)

        ax.set_yticks(np.arange(0, len(hail_classes)), labels=hail_class_names, fontsize=8)
        ax.set_ylim(-0.5, len(hail_classes)-0.5)

        if ax.get_subplotspec().is_last_row():
          ax.set_xlabel("minimum number of pixels")

        if not ax.get_subplotspec().is_first_col():
          ax.set_yticklabels([])
      except IndexError:
        pass

  # plt.tight_layout()

  if output_name is not None:
    plt.savefig(output_name, bbox_inches='tight')
    plt.close()
  else:
    plt.show()
    plt.close()

def plot_files_per_min_pixel_and_areathresh_for_hailclasses(overpass_hailclass_area, area_thresh, 
                                                            year_start=2006, output_name=None):
 # number of area thresholds
  N_thresh = len(area_thresh)
  colors = plt.cm.viridis(np.linspace(0, 1, N_thresh))

  # filter for year_start
  overpass_hailclass_area = overpass_hailclass_area.sel(year=slice(year_start, None))
  # sum over years
  overpass_hailclass_area = overpass_hailclass_area.sum(dim="year")

  # get hail class names
  hail_class_names = mwcch_read.get_hail_classes(type="name")

  # create figure 
  f, axes = plt.subplots(len(hail_class_names))
  f.set_figheight(10)
  f.set_figwidth(10)

  # loop over area thresholds
  for t, thresh in enumerate(area_thresh):

    # select only overpasses with certain area threshold and sum over all areas
    area_filtered_data = \
      overpass_hailclass_area.where(overpass_hailclass_area['area_perc'] >= thresh, drop=True)

    # get number of overpasses per year and hail_class
    hail_counts = area_filtered_data.N_overpasses.sum(dim=["area_perc"])

    # loop over hail class
    for hail in hail_counts.hail_class.values:
      # get axis for this hail class
      ax = axes[int(hail)]

      # get percentage of overpasses containing this hail class
      n_class = hail_counts.sel(hail_class=hail).values
      
      # draw development over the years for this hail class
      ax.plot(hail_counts.min_pixel.values, n_class, 
              color=colors[t], #mwcch_plt.hail_class_colors_list[int(hail)], 
              #alpha=1-t*(0.6 / N_thresh), linestyle="-", 
              label=f">={thresh}%")
      
      if t == 0:
        # add hail class text in the bottom left corner
        ax.text(0.2, 0.9, mwcch_read.get_hail_classes(type='name')[int(hail)], 
            transform=ax.transAxes, fontsize=10, verticalalignment='bottom',
            color="k")
  
  # format x axes
  for ax in axes:
    if ax == axes[0]:
      ax.legend(loc=0, frameon=True)
    if ax == axes[-1]:
      ax.set_xlabel("minimum number of pixels")
    ax.set_xticks(hail_counts.min_pixel.values)
    ax.set_xlim(hail_counts.min_pixel.values[0]-0.5, hail_counts.min_pixel.values[-1]+0.5)
    if ax != axes[-1]:
      ax.set_xticklabels([])
    ax.set_ylabel("number of files")
    ax.grid(True)

  plt.tight_layout()

  if output_name is not None:
    plt.savefig(output_name, bbox_inches='tight')
    plt.close()
  else:
    plt.show()
    plt.close()

# %%
if __name__ == "__main__":
  # print("plot hail class occurrence per area for 1999-2023")
  # occurrence_per_area_fraction(np.arange(1999, 2024, 1))
  # print("plot hail class occurrence per area for 2006-2023")
  # occurrence_per_area_fraction(np.arange(2006, 2024, 1))

  # print("plot hail class occurrence per year and covered area")
  # occurrence_per_year_and_coveredarea()

  # print("plot hail class development per area thresholds")
  # hailclass_development_per_area_thresholds()

  # print("plot hail class distribution per area thresholds for 1999-2023")
  # hailclass_distribution_per_area_thresholds(np.arange(1999, 2024, 1))
  # print("plot hail class distribution per area thresholds for 2006-2023")
  # hailclass_distribution_per_area_thresholds(np.arange(2006, 2024, 1))

  # print("plot hail class distribution and development for area threshold")
  # hailclass_distribution_and_development_for_area_threshold()

  # print("plot overpasses per satellite, year and area threshold")
  # hailclass_overpass_per_satellite_year_and_area_threshold()

  print("plot hail class distribution per min pixel for different area thresholds")
  hailclass_distribution_per_min_pixel_for_areathresh()


# %%
