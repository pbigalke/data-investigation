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
import plotting.plot_MWCC_H as mwcch_plt

datapath = mwcch_read.MWCCH_MSGGRID_PATH

def load_counter_file(counter_filename):
  if os.path.exists(counter_filename):
    print("thingy is here")
    with xr.load_dataset(counter_filename) as counter:
      return counter
  return None

# %%
# plot hail class occurrence per area 
def occurrence_per_area_fraction():
  # define plot path and file name of specific counter file
  plotpath = "/net/merisi/pbigalke/plots/data_investigation/MWCC-H_new_in_domain"
  counter_file = f"{datapath}/overpasses_per_hailclass_area.nc"
  overpass_hailclass_area = load_counter_file(counter_file)

  out = f"{plotpath}/area_covered_by_overpasses.png"
  barplot_occurrences_per_area_fraction(overpass_hailclass_area, output_name=out, figsize=(8, 8),
                                        fraction=False, log=False)
  out_log = f"{plotpath}/area_covered_by_overpasses_log.png"
  barplot_occurrences_per_area_fraction(overpass_hailclass_area, output_name=out_log, figsize=(8, 8),
                                        fraction=False, log=True)
  out_frac = f"{plotpath}/area_covered_by_overpasses_frac.png"
  barplot_occurrences_per_area_fraction(overpass_hailclass_area, output_name=out_frac, figsize=(8, 8),
                                        fraction=True, log=False)
  out_frac_log = f"{plotpath}/area_covered_by_overpasses_frac_log.png"
  barplot_occurrences_per_area_fraction(overpass_hailclass_area, output_name=out_frac_log, figsize=(8, 8),
                                        fraction=True, log=True)

def barplot_occurrences_per_area_fraction(overpass_hailclass_area, output_name=None, figsize=(10, 8),
                                          fraction=False, log=False):
  
  f, ax = plt.subplots(1)
  f.set_figheight(figsize[1])
  f.set_figwidth(figsize[0])
  ax.set_title("distribution of covered area fraction")

  # get total number of overpasses in dataset
  N_total = overpass_hailclass_area.N_overpasses.sum().values

  # get hail class names
  hail_class_names = mwcch_read.get_hail_class(poh=None, type="name")

  # define bottom of barplots
  bottom = np.zeros(overpass_hailclass_area.area_perc.shape)

  # loop over hail classes and fill in barplots
  for h in overpass_hailclass_area.hail_class.values:

    # get counts only for this hail_class
    area_counts = overpass_hailclass_area.sel(hail_class=h).values

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

  # format y axes
  ax.set_ylabel("fraction of all overpasses" if fraction else "number of overpasses")
  if log:
    ax.set_yscale('log')
  ax.grid()

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
  plotpath = "/net/merisi/pbigalke/plots/data_investigation/MWCC-H_hail_occurrence"
  counter_file = f"{datapath}/overpasses_per_year_hailclass_area.nc"
  overpass_year_hailclass_area = load_counter_file(counter_file)

  year_start = [1999, 2006]
  for y in year_start:
    out = f"{plotpath}/hail_occurrence_per_area_thresh_and_year_{y}onwards.png"
    hailclass_percentage_per_area_thresh_and_year(overpass_year_hailclass_area, year_start=y, output_name=out)

def hailclass_percentage_per_area_thresh_and_year(overpass_year_hailclass_area, year_start=1999, output_name=None):
  
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
    # ax.set_title(f"{mwcch_read.get_hail_class(type='name')[int(hail)]}")

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
    ax.text(0.01, 0.01, mwcch_read.get_hail_class(type='name')[int(hail)], 
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
  plotpath = "/net/merisi/pbigalke/plots/data_investigation/MWCC-H_hail_occurrence"
  counter_file = f"{datapath}/overpasses_per_year_hailclass_area.nc"
  overpass_year_hailclass_area = load_counter_file(counter_file)

  # different thresholds
  area_thresh = [10, 20, 30, 40, 50, 60]
  out = f"{plotpath}/hail_class_development_per_areathresh.png"
  plot_hailclass_development_per_areathresh(overpass_year_hailclass_area, area_thresh, 
                                            output_name=out)

def plot_hailclass_development_per_areathresh(overpass_year_hailclass_area, area_thresh, output_name=None, 
                                              figsize=(10, 15)):
  
  # number of area thresholds
  N_thresh = len(area_thresh)
  colors = plt.cm.viridis(np.linspace(0, 1, N_thresh))

  # get hail class names
  hail_class_names = mwcch_read.get_hail_class(type="name")

  # create figure 
  f, axes = plt.subplots(len(hail_class_names))
  f.set_figheight(figsize[1])
  f.set_figwidth(figsize[0])

  # loop over area thresholds
  for t, thresh in enumerate(area_thresh):

    # select only overpasses with certain area threshold and sum over all areas
    area_filtered_data = \
      overpass_year_hailclass_area.where(overpass_year_hailclass_area['area_perc'] >= thresh, drop=True)

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
        ax.text(0.2, 0.9, mwcch_read.get_hail_class(type='name')[int(hail)], 
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
def hailclass_distribution_per_area_thresholds():
  # define plot path and file name of specific counter file
  plotpath = "/net/merisi/pbigalke/plots/data_investigation/MWCC-H_hail_occurrence"
  counter_file = f"{datapath}/overpasses_per_hailclass_area.nc"
  overpass_hailclass_area = load_counter_file(counter_file)

  # different thresholds
  area_thresh = [10, 20, 30, 40, 50, 60]
  out = f"{plotpath}/hail_class_distribution_per_areathresh.png"
  plot_hailclass_distribution_per_areathresh(overpass_hailclass_area, area_thresh=area_thresh, output_name=out)

def plot_hailclass_distribution_per_areathresh(overpass_hailclass_area, area_thresh, output_name=None, 
                                               figsize=(15, 6)):
  
  f, ax1 = plt.subplots(1, layout='constrained')
  f.set_figheight(figsize[1])
  f.set_figwidth(figsize[0])
  # ax1.set_title("distribution of hail classes per area threshold")

  # get hail class names
  hail_class_names = mwcch_read.get_hail_class(type="name")

  # loop over area thresholds
  for t, thresh in enumerate(area_thresh):

    # set x positions for bars
    x_positions = np.arange(0, len(overpass_hailclass_area.hail_class), 1) + t * 0.15

    # select only overpasses with certain area threshold and sum over all areas
    area_filtered_data = overpass_hailclass_area.where(overpass_hailclass_area['area_perc'] >= thresh, drop=True)

    # get number of overpasses per hail_class over all areas
    hail_counts = area_filtered_data.N_overpasses.sum(dim=["area_perc"])

    # get total number of overpasses in dataset
    N_total = hail_counts.sum().values
      
    # get total number and percentage of overpasses containing this hail class
    n_class = hail_counts.values / N_total * 100
    
    # plot bar for this class
    ax1.bar(x_positions, n_class, 0.13, 
            color=mwcch_plt.hail_class_colors_list, 
            align="center")
    
  # set x ticks for area thresholds
  x_thresh = np.arange(0, len(hail_class_names), 1)
  thresh_ticks = np.sort(np.concatenate([x_thresh + 0.15 * t for t in range(len(area_thresh))]))
  thresh_tick_labels = [f">{l}%" for l in np.tile(area_thresh, len(hail_class_names)).flatten()]
  ax1.set_xticks(thresh_ticks, labels=thresh_tick_labels) #, rotation=45, ha='right')

  # second ticks for the class names
  sec = ax1.secondary_xaxis(location='top')
  x_class = np.arange(0, len(hail_class_names), 1) + 0.15 * (len(area_thresh) / 2. - 0.5)
  sec.set_xticks(x_class, labels=hail_class_names)

  # format the rest of the axes
  ax1.set_xlim(-0.15, len(hail_class_names))
  ax1.set_ylabel("occurrence [%]")
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
  plotpath = "/net/merisi/pbigalke/plots/data_investigation/MWCC-H_hail_occurrence"
  counter_file = f"{datapath}/overpasses_per_year_hailclass_area.nc"
  overpass_year_hailclass_area = load_counter_file(counter_file)

  # loop over different thresholds
  for t in [50, 60]:  #0, 10, 20, 30, 40]:

    out = f"{plotpath}/hail_class_distribution_development_areathresh{t}.png"
    plot_hailclass_distribution_and_development(overpass_year_hailclass_area, 
                                                area_threshold=t, output_name=out)

    out_only_hail = f"{plotpath}/hail_class_distribution_development_areathresh{t}_onlyhail.png"
    plot_hailclass_distribution_and_development(overpass_year_hailclass_area, 
                                                area_threshold=t, output_name=out_only_hail, only_hail=True)

def plot_hailclass_distribution_and_development(overpass_year_hailclass_area, area_threshold=0, output_name=None, 
                                                figsize=(15, 5), fraction=False, only_hail=False):
  
  f, (ax1, ax2) = plt.subplots(1, 2, width_ratios=[1,2])
  f.set_figheight(figsize[1])
  f.set_figwidth(figsize[0])
  ax1.set_title("distribution of hail classes")
  ax2.set_title("hail classes over the years")

  # select only overpasses with certain area threshold and sum over all areas
  area_filtered_data = overpass_year_hailclass_area.where(overpass_year_hailclass_area['area_perc'] >= area_threshold, drop=True)

  # get number of overpasses per year and hail_class
  yearly_hail_counts = area_filtered_data.N_overpasses.sum(dim=["area_perc"])

  # get total number of overpasses in dataset
  N_total = yearly_hail_counts.sum().values

  # get total number of overpasses per year
  N_total_yearly = yearly_hail_counts.sum(dim=["hail_class"]).values

  # get hail class names
  hail_class_names = mwcch_read.get_hail_class(type="name")

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
def hailclass_per_satellite_and_area_threshold():
  # define plot path and file name of specific counter file
  plotpath = "/net/merisi/pbigalke/plots/data_investigation/MWCC-H_hail_occurrence"
  counter_file = f"{datapath}/overpasses_per_year_hour_hailclass_covered_area_sat.nc"
  overpass_satellite_area = load_counter_file(counter_file)
  print(overpass_satellite_area)

  out = f"{plotpath}/overpasses_per_satellite_and_areathresh.png"
  # hailclass_percentage_per_area_thresh_and_satellite(overpass_satellite_area, output_name=out)

def hailclass_percentage_per_area_thresh_and_satellite(overpass_hailclass_hour_area_sat, output_name=None):
  
  # sum over all hours
  overpass_hailclass_area_sat = overpass_hailclass_hour_area_sat.sum(dim=["hour"])

  # get hail classes  
  hail_classes = overpass_hailclass_area_sat.hail_class.values 

  # get satellite names
  sats = overpass_hailclass_area_sat.sat.values

  # regroup data by larger area bins
  # Step 1: Define the new bins
  new_area_bins = np.arange(0, 110, 10)
  # Step 2: Group the data by the new bins
  grouped = overpass_hailclass_area_sat.groupby_bins('area_perc', new_area_bins, right=True)
  # Step 3: Aggregate the counts within each new bin
  aggregated_counts = grouped.sum()
  # get total number of overpasses per sat and area_bin
  total_overpasses = aggregated_counts.sum(dim=["hail_class"]).N_overpasses.values

  # create figure with gridspec
  fig = plt.figure(figsize=(4, 2*(len(hail_classes)+1)))
  gs = mpl.gridspec.GridSpec(len(hail_classes)+1, 2, width_ratios=[20, 1], 
                             hspace=0.3, wspace=0)

  # first plot total number of overpasses per area bin and sat
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
    # ax.set_title(f"{mwcch_read.get_hail_class(type='name')[int(hail)]}")

    # get number of overpasses per area bin and year
    n_hail = aggregated_counts.where(aggregated_counts.hail_class == hail, drop=True)
    perc_hail = n_hail.N_overpasses.values[:, :, 0] / total_overpasses * 100
    # Replace NaN values with zero
    perc_hail[np.isnan(perc_hail)] = 0

    # plot percentage of hail class per area bin and year
    c = ax.imshow(perc_hail, cmap="inferno", origin="lower")#, 
                  # vmin=0, vmax=vmax)
    cbar_ax = fig.add_subplot(gs[int(hail)+1, 1])
    fig.colorbar(c, cax=cbar_ax, label="Occurrence [%]")

    # add hail class text in the bottom left corner
    ax.text(0.01, 0.01, mwcch_read.get_hail_class(type='name')[int(hail)], 
            transform=ax.transAxes, fontsize=10, verticalalignment='bottom',
            color="white")

    # format axes
    for ax in fig.get_axes():
      if ax.get_subplotspec().is_first_col():
        ax.set_yticks(np.arange(0, len(new_area_bins))-0.5, labels=new_area_bins, fontsize=8)
        ax.set_ylim(-0.5, len(new_area_bins)-1.5)
        ax.set_ylabel("area [%]")
        ax.set_xticks(np.arange(0, len(sats), 1)-0.5, 
                      labels=sats, rotation=-45, ha='left', fontsize=8)
        ax.set_xlim(-0.5, len(sats)-0.5)
        if not ax.get_subplotspec().is_last_row():
          ax.set_xticklabels([]) 
        else:
          ax.set_xlabel("satellites")

  # plt.tight_layout()

  if output_name is not None:
    plt.savefig(output_name, bbox_inches='tight')
    plt.close()
  else:
    plt.show()
    plt.close()



# %%
if __name__ == "__main__":
  # occurrence_per_area_fraction()
  # occurrence_per_year_and_coveredarea()
  # hailclass_development_per_area_thresholds()
  # hailclass_distribution_per_area_thresholds()
  # hailclass_distribution_and_development_for_area_threshold()
  hailclass_per_satellite_and_area_threshold()
# %%
