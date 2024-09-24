# %%
import glob
import xarray as xr
import numpy as np
import datetime
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patches as mpatches
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
import os
import sys
sys.path.append("..")
import matching_data.collect_matching_files as clct
import readers.read_processed_MWCC_H as mwcch_read
import MWCCH_overview_plots as mwcch_plt
from config.domain_info import domain_expats

hail_class_colors = {'no_hail': 'whitesmoke', 
                    'hail_potential': 'lightgrey', 
                    'hail_initiation_graupel': 'cyan', 
                    'large_hail': 'darkcyan',
                    'super_hail': 'lime'}
hail_class_colors2 = {'no_hail': mpl.cm.get_cmap('Greys')(0.2), 
                    'hail_potential': mpl.cm.get_cmap('Greys')(0.3), 
                    'hail_initiation_graupel': mpl.cm.get_cmap('cool')(0), 
                    'large_hail': mpl.cm.get_cmap('cool')(0.5),
                    'super_hail': mpl.cm.get_cmap('cool')(0.9)}
hail_class_cmap = {}
hail_classes = mwcch_read.get_hail_class()
cmap = mpl.cm.get_cmap('BuPu')
clrs = [cmap(c) for c in np.linspace(0.1, 1, len(hail_classes))]
for h, hail in enumerate(hail_classes):
  hail_class_cmap[hail] = clrs[h]


# %%
def count_max_mean_hail_levels(path, years, months, hail_levels, 
                                output_filename="occurrence_max_mean_hail_per_month_and_satellite",
                                overwrite=False):

  counter_filename = f"{path}/{output_filename}.nc"

  if os.path.exists(counter_filename) and not overwrite:
    print("thingy is here")
    with xr.load_dataset(counter_filename) as counter:
      return counter
  
  else:
    # choords
    sat = ['meto01', 'meto02', 'meto03', 'noaa15', 'noaa16', 'noaa17', 'noaa18', 'noaa19', 'n20', 'n21', 'npp', 'f16', 'f17', 'gpm']
    max_poh = np.zeros((len(sat), len(years), len(months), len(hail_levels)))
    mean_poh = np.zeros((len(sat), len(years), len(months), len(hail_levels)))
    instr = ['MHS', 'MHS', 'MHS', 'MHS', 'MHS', 'MHS', 'MHS', 'MHS', 'ATMS', 'ATMS', 'ATMS', 'SSMIS', 'SSMIS', 'GMI']
    color = ['g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'b', 'b', 'b', 'r', 'r', 'orange']
    
    count_hail = xr.Dataset(
      data_vars=dict(
          N_max_poh=(["sat", "year", "month", "hail_level"], max_poh),
          N_mean_poh=(["sat", "year", "month", "hail_level"], mean_poh),
          instrument=(["sat"], instr), 
          color=(["sat"], color), 
      ),
      coords=dict(
          sat=("sat", sat),
          year=("year", years),
          month=("month", months),
          hail_level=("hail_level", hail_levels),
      ),
    )

    total_n_files = len(glob.glob(f"{path}/*/*/*/*.nc"))
    print("total number of files: ", total_n_files, flush=True)
    files_processed = 0

    # loop over years
    for year in years:

      # loop over months
      for month in months:
        
        path_month = f"{path}/{year}/{month:02}"
        files = glob.glob(f"{path_month}/*/*.nc")
        
        if len(files) > 0:
          for f in files:

            if files_processed % 1000 == 0:
              print(f"{files_processed}/{total_n_files}", flush=True)

            # find sat name from filepath
            sat = mwcch_read.get_sat_from_filepath(f)

            # read in hail probability data
            poh = mwcch_read.read(f).POH.values

            # find maximum hail probability in this timestamp
            max_poh = np.max(poh)
            idx_max = np.searchsorted(hail_levels, max_poh, side='left')
            max_level = hail_levels[idx_max]

            # increase counter at specific sat, year, month and hail_level
            count_hail.N_max_poh.loc[dict(sat=sat, year=year, month=month, hail_level=max_level)] += 1

            # find mean hail probability in this timestamp (of non-zero pixels)
            mask_hail = poh > 0
            if np.sum(mask_hail) > 0:
              mean_poh = np.mean(poh[mask_hail])
              idx_mean = np.searchsorted(hail_levels, mean_poh, side='left')
              mean_level = hail_levels[idx_mean]
            else:
              mean_level = hail_levels[0]
      
            # increase counter at specific sat, year, month and hail_level
            count_hail.N_mean_poh.loc[dict(sat=sat, year=year, month=month, hail_level=mean_level)] += 1
            
            # count number of processed files
            files_processed += 1

    # save to file so that we don't need to run this again while creating the plots
    count_hail.to_netcdf(counter_filename)
    return count_hail
  
def get_hail_class(poh=None):
  hail_classes = ["no_hail", 
                  "hail_potential", 
                  "hail_initiation_graupel", 
                  "large_hail", 
                  "super_hail"]
  if poh is None:
    return hail_classes
  else:
    if 0 <= poh < 0.2:
      return hail_classes[0]
    elif 0.2 <= poh < 0.36:
      return hail_classes[1]
    elif 0.36 <= poh < 0.45:
      return hail_classes[2]
    elif 0.45 <= poh < 0.6:
      return hail_classes[3]
    elif 0.6 <= poh <= 1.0:
      return hail_classes[4]
    else:
      return None
    
def get_hail_class_boundaries():
  return [0, 0.2, 0.36, 0.45, 0.6, 1.0]

def count_max_mean_hail_classes(path, years, months,
                                output_filename="occurrence_max_mean_hail_classes",
                                overwrite=False):

  counter_filename = f"{path}/{output_filename}.nc"
  if os.path.exists(counter_filename) and not overwrite:
    print("thingy is here")
    with xr.load_dataset(counter_filename) as counter:
      return counter
  
  else:
    # choords
    hail_classes = mwcch_read.get_hail_class()
    sat = ['meto01', 'meto02', 'meto03', 'noaa15', 'noaa16', 'noaa17', 'noaa18', 'noaa19', 'n20', 'n21', 'npp', 'f16', 'f17', 'gpm']
    max_poh_class = np.zeros((len(sat), len(years), len(months), len(hail_classes)))
    mean_poh_class = np.zeros((len(sat), len(years), len(months), len(hail_classes)))
    instr = ['MHS', 'MHS', 'MHS', 'MHS', 'MHS', 'MHS', 'MHS', 'MHS', 'ATMS', 'ATMS', 'ATMS', 'SSMIS', 'SSMIS', 'GMI']
    color = ['g', 'g', 'g', 'g', 'g', 'g', 'g', 'g', 'b', 'b', 'b', 'r', 'r', 'orange']
    
    count_hail = xr.Dataset(
      data_vars=dict(
          N_max_poh=(["sat", "year", "month", "hail_class"], max_poh_class),
          N_mean_poh=(["sat", "year", "month", "hail_class"], mean_poh_class),
          instrument=(["sat"], instr), 
          color=(["sat"], color), 
      ),
      coords=dict(
          sat=("sat", sat),
          year=("year", years),
          month=("month", months),
          hail_class=("hail_class", hail_classes),
      ),
    )

    total_n_files = len(clct.get_files_in_study_period(path, years, months=months))
    print("total number of files: ", total_n_files, flush=True)
    files_processed = 0

    # loop over years
    for year in years:

      # loop over months
      for month in months:
        
        path_month = f"{path}/{year}/{month:02}"
        files = glob.glob(f"{path_month}/*/*.nc")
        
        if len(files) > 0:
          for f in files:

            if files_processed % 1000 == 0:
              print(f"{files_processed}/{total_n_files}", flush=True)

            # find sat name from filepath
            sat = mwcch_read.get_sat_from_filepath(f)

            # read in hail probability data
            poh = mwcch_read.read(f).POH.values

            # find maximum hail probability in this timestamp
            max_poh = np.max(poh)
            max_hail_class = get_hail_class(max_poh)

            # increase counter at specific sat, year, month and hail_level
            count_hail.N_max_poh.loc[dict(sat=sat, year=year, month=month, hail_class=max_hail_class)] += 1

            # find mean hail probability in this timestamp (of non-zero pixels)
            mask_hail = poh > 0
            if np.sum(mask_hail) > 0:
              mean_poh = np.mean(poh[mask_hail])
              mean_hail_class = get_hail_class(mean_poh)
            else:
              mean_hail_class = get_hail_class(0)
      
            # increase counter at specific sat, year, month and hail_level
            count_hail.N_mean_poh.loc[dict(sat=sat, year=year, month=month, hail_class=mean_hail_class)] += 1
            
            # count number of processed files
            files_processed += 1

    # print total number of files in this study period
    print("total number of files processed: ", files_processed, flush=True)

    # save to file so that we don't need to run this again while creating the plots
    count_hail.to_netcdf(counter_filename)
    return count_hail

# %%
def barplot_occurrences_per_hail_level(hail_counter, output_name=None, figsize=(10, 10), log=False):
  
  x_level = np.arange(0, len(hail_counter.hail_level), 1)

  f, (ax1, ax2) = plt.subplots(2, sharex=True)
  f.set_figheight(figsize[1])
  f.set_figwidth(figsize[0])
  ax1.set_title("maximum hail probability of overpasses", y=1.0, pad=-14)
  ax2.set_title("mean hail probability of overpasses", y=1.0, pad=-14)

  # get total number of overpasses in dataset
  N_total = hail_counter.N_max_poh.sum().values

  # add over each bar the percentage of all overpasses
  for h, hail in enumerate(hail_counter.hail_level):
    hail_level_counts = hail_counter.loc[dict(hail_level=hail)].sum()

    # add maximum hail events from this satellite to bar plot
    ax1.bar(x_level[h], hail_level_counts.N_max_poh.values, -0.8, 
            color="r", align="edge")
    
    # add percentage above max poh bars
    perc_max = hail_level_counts.N_max_poh.values / N_total * 100
    ax1.text(h, 1 if perc_max == 0 else hail_level_counts.N_max_poh.values, f'{perc_max:.2f}', fontsize=12, 
             horizontalalignment='right', verticalalignment='bottom')
    
    # add mean hail events from this satellite  to bar plot
    ax2.bar(x_level[h], hail_level_counts.N_mean_poh.values, -0.8, 
            color="b", align="edge")
    
    # add percentage above mean poh bars
    perc_mean = hail_level_counts.N_mean_poh.values / N_total * 100
    ax2.text(h, 1 if perc_mean == 0 else hail_level_counts.N_mean_poh.values, f'{perc_mean:.2f}', fontsize=12, 
             horizontalalignment='right', verticalalignment='bottom')
    
  # format axis 1
  ax1.set_ylabel("number of files")
  if log:
    ax1.set_yscale('log')
  ax1.grid()

  # format axis 2
  ax2.set_xticks(x_level, labels=hail_counter.hail_level.values)
  ax2.set_xlim(-0.8, len(x_level)-1)
  ax2.set_xlabel("hail probability")
  ax2.set_ylabel("number of files")
  if log:
    ax2.set_yscale('log')
  ax2.grid()

  plt.tight_layout()

  if output_name is not None:
    plt.savefig(output_name, bbox_inches='tight')
    plt.close()
  else:
    plt.show()
    plt.close()

def plot_occurrences_per_hail_class(hail_counter, output_name=None, figsize=(10, 5),
                                    fraction=False, log=False):
  
  f, (ax1, ax2) = plt.subplots(1, 2)
  f.set_figheight(figsize[1])
  f.set_figwidth(figsize[0])
  ax1.set_title("distribution of hail classes")
  ax2.set_title("cumulative distribution of hail classes")

  # get total number of overpasses in dataset
  N_total = hail_counter.N_max_poh.sum().values

  # get total amount of files per hail class
  hail_class_counts = hail_counter.N_max_poh.sum(dim=["sat", "year", "month"])
  for h, hail in enumerate(hail_class_counts.hail_class.values):
    
    # get total number and percentage of overpasses containing this hail class
    n_class = hail_class_counts.sel(hail_class=hail).values
    perc_class = n_class / N_total * 100 
    if fraction:
      n_class = perc_class
    
    # plot bar for this class
    ax1.bar(h, n_class, -0.8, color=hail_class_colors[hail], align="center")

    # add percentage above max poh bars
    position = 1 if n_class == 0 else n_class
    ax1.text(h, position, f'{perc_class:.2f}', fontsize=12, 
              horizontalalignment='center', verticalalignment='bottom')

  # add number of events of this hail class to cumulative bar plot
  x_edge = np.arange(0, len(hail_counter.hail_class)+1, 1)
  x_cumul = np.concatenate((x_edge[:1], np.repeat(x_edge[1:-1], 2), x_edge[-1:]))
  y_cumul = np.repeat(np.cumsum(hail_class_counts.values), 2)
  y_cumul_back = np.repeat(np.cumsum(hail_class_counts.values[::-1])[::-1], 2)
  ax2.plot(x_cumul, y_cumul, color="b", linestyle="--")
  ax2.plot(x_cumul, y_cumul_back, color="b", linestyle="-")

  # format x axes
  x_center = np.arange(0, len(hail_counter.hail_class), 1)
  ax1.set_xticks(x_center, labels=hail_counter.hail_class.values, rotation=45, ha='right')
  ax1.set_xlim(x_center[0]-0.5, x_center[-1] + 0.5)
  #
  ax2.set_xticks(x_edge, labels=get_hail_class_boundaries())
  ax2.set_xlim(x_edge[0], x_edge[-1])
  ax2.set_xlabel("hail probability")

  # format y axes
  for ax in [ax1, ax2]:
    ax.set_ylabel("fraction of all files" if fraction else "number of files")
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
datapath = mwcch_read.MWCCH_PATH
print(datapath)

plotpath = "/net/merisi/pbigalke/plots/data_investigation/MWCC-H_hail_occurrence"
if not os.path.exists(plotpath):
    os.makedirs(plotpath)
years = np.arange(1999, 2024, 1).astype(int)
months = np.arange(4, 10, 1).astype(int)
# all_files = clct.get_files_in_study_period(datapath, years, months)
# print(len(all_files))

hail_levels = np.array([0, .1, .15, .2, .25, .3, .36, .4, .5, .6, .7, .8, .9, 1])

# count the maximum hail occurrence in all files
hail_level_counter = count_max_mean_hail_levels(datapath, years, months, hail_levels, overwrite=False)
hail_class_counter = count_max_mean_hail_classes(datapath, years, months, overwrite=False)

# # plot occurrences of max hail per hail level
# hail_level_out = f"{plotpath}/max_mean_hail_distribution.png"
# barplot_occurrences_per_hail_level(hail_level_counter, output_name=hail_level_out, figsize=(10, 10), log=False)
# hail_level_log_out = f"{plotpath}/max_mean_hail_distribution_log.png"
# barplot_occurrences_per_hail_level(hail_level_counter, output_name=hail_level_log_out, figsize=(10, 10), log=True)

# plot occurrences of max hail per year and hail class
hail_class_out = f"{plotpath}/max_hail_class_distribution.png"
plot_occurrences_per_hail_class(hail_class_counter, output_name=None, #hail_class_out, 
                                log=False, fraction=False)
# hail_class_out_log = f"{plotpath}/max_hail_class_distribution_log.png"
# plot_occurrences_per_hail_class(hail_class_counter, output_name=hail_class_out_log, 
#                                 log=True, fraction=False)
# hail_class_out_frac = f"{plotpath}/max_hail_class_distribution_frac.png"
# plot_occurrences_per_hail_class(hail_class_counter, output_name=hail_class_out_frac, 
#                                 log=False, fraction=True)
# hail_class_out_frac_log = f"{plotpath}/max_hail_class_distribution_frac_log.png"
# plot_occurrences_per_hail_class(hail_class_counter, output_name=hail_class_out_frac_log, 
#                                 log=True, fraction=True)
# %%
