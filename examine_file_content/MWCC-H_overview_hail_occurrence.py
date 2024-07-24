# %%
import glob
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
import os
import sys
sys.path.append("..")
import matching_data.collect_matching_files as clct
import readers.read_processed_MWCC_H as mwcch_read
import MWCCH_overview_plots as mwcch_plt

# %%
def count_max_mean_hail_occurrence(path, years, months, hail_levels, overwrite=False):

  counter_filename = f"{path}/occurrence_max_mean_hail_per_month_and_satellite.nc"

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
      
            # increase counter at specific sat, year, month and hail_level
            count_hail.N_mean_poh.loc[dict(sat=sat, year=year, month=month, hail_level=mean_level)] += 1
            
            # count number of processed files
            files_processed += 1

    # save to file so that we don't need to run this again while creating the plots
    count_hail.to_netcdf(counter_filename)
    return count_hail

def plot_occurrences_per_hail_level(hail_counter, output_name=None, figsize=(10, 10), log=False):
  
  x_level = np.arange(0, len(hail_counter.hail_level), 1)

  f, (ax1, ax2) = plt.subplots(2, sharex=True)
  f.set_figheight(figsize[1])
  f.set_figwidth(figsize[0])
  ax1.set_title("mean hail probability of overpasses", y=1.0, pad=-14)
  ax2.set_title("maximum hail probability of overpasses", y=1.0, pad=-14)

  # get total number of overpasses in dataset
  N_total = hail_counter.N_max_poh.sum().values

  # loop over satellites
  bottom_mean = np.zeros(len(hail_counter.hail_level))
  bottom_max = np.zeros(len(hail_counter.hail_level))

  for sat in hail_counter.sat:
      hail_sat = hail_counter.loc[dict(sat=sat)].sum(dim=("year", "month"))
      
      # add mean hail events from this satellite  to bar plot
      ax1.bar(x_level, hail_sat.N_mean_poh.values, -0.8, 
              color=f"{hail_sat.color.values}", bottom=bottom_mean, align="edge")
      bottom_mean += hail_sat.N_mean_poh.values

      # add maximum hail events from this satellite to bar plot
      ax2.bar(x_level, hail_sat.N_max_poh.values, -0.8, 
              color=f"{hail_sat.color.values}", bottom=bottom_max, align="edge")
      bottom_max += hail_sat.N_max_poh.values
    
  # add over each bar the percentage of all overpasses
  for h, hail in enumerate(hail_counter.hail_level):
    hail_level_counts = hail_counter.loc[dict(hail_level=hail)].sum()
    
    # add percentage above mean poh bars
    perc_mean = hail_level_counts.N_mean_poh.values / N_total * 100
    ax1.text(h, 1 if bottom_mean[h] == 0 else bottom_mean[h], f'{perc_mean:.2f}', fontsize=12, 
             horizontalalignment='right', verticalalignment='bottom')
    
    # add percentage above max poh bars
    perc_max = hail_level_counts.N_max_poh.values / N_total * 100
    ax2.text(h, 1 if bottom_max[h] == 0 else bottom_max[h], f'{perc_max:.2f}', fontsize=12, 
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

  # Put a legend below current axis
  legend_patches = [mpatches.Patch(color='g', label='MHS'), 
                    mpatches.Patch(color='b', label='ATMS'), 
                    mpatches.Patch(color='r', label='SSMIS'), 
                    mpatches.Patch(color='orange', label='GMI')]
  ax1.legend(handles=legend_patches, 
            loc='upper right', bbox_to_anchor=(0.98, 0.98),
            fancybox=True, shadow=True, ncol=1)

  plt.tight_layout()

  if output_name is not None:
    plt.savefig(output_name, bbox_inches='tight')
    plt.close()
  else:
    plt.show()
    plt.close()

# %%
datapath = "/net/merisi/pbigalke/data/MWCC-H/netcdf"
plotpath = "/net/merisi/pbigalke/plots/data_investigation/MWCC-H_hail_occurrence"
if not os.path.exists(plotpath):
    os.makedirs(plotpath)
years = np.arange(1999, 2024, 1).astype(int)
months = np.arange(4, 10, 1).astype(int)
# all_files = clct.get_files_in_study_period(datapath, years, months)
# print(len(all_files))

hail_levels = np.array([0, .1, .15, .2, .25, .3, .36, .4, .5, .6, .7, .8, .9, 1])

# count the maximum hail occurrence in all files
hail_counter = count_max_mean_hail_occurrence(datapath, years, months, hail_levels, 
                                              overwrite=False)

# plot occurrences of max hail per year and hail level
hail_level_out = f"{plotpath}/max_mean_hail_distribution.png"
plot_occurrences_per_hail_level(hail_counter, output_name=hail_level_out, figsize=(10, 10), log=False)
hail_level_log_out = f"{plotpath}/max_mean_hail_distribution_log.png"
plot_occurrences_per_hail_level(hail_counter, output_name=hail_level_log_out, figsize=(10, 10), log=True)
# %%
