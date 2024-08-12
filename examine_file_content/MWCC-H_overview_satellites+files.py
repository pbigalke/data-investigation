# %%
import glob
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
import os
import sys
sys.path.append("..")
import readers.read_processed_MWCC_H as mwcch_read
import matching_data.collect_matching_files as match
import MWCCH_overview_plots as mwcch_plt

def plot_satellites_contribution_and_number_of_files():
  datapath = "/net/merisi/pbigalke/data/MWCC-H/netcdf"
  plotpath = "/net/merisi/pbigalke/plots/data_investigation/MWCC-H_new_in_domain"
  if not os.path.exists(plotpath):
     os.makedirs(plotpath)
  years = np.arange(1999, 2024, 1)
  months = np.arange(4, 10, 1)

  # count number of files per year, month and satellite
  satellites = count_overpass_occurrences_expats_domain(datapath, years, months)

  # plot satellite deployment overview
  sat_overview = f"{plotpath}/sat_overview_apr-sep_expatsdomain.png"
  # sat_overview = f"{plotpath}/sat_overview.png"
  mwcch_plt.plot_satellite_deployment_overview(years, months, satellites, sat_overview, figsize=(20, 6))

  # plot occurence per month
  overpasses_month = f"{plotpath}/overpasses_per_month_apr-sep_expatsdomain.png"
  # overpasses_month = f"{plotpath}/overpasses_per_month.png"
  mwcch_plt.plot_occurrences_per_month(years, months, satellites, overpasses_month, figsize=(25, 6))

  # plot occurence per month and satellite
  overpasses_sat_month = f"{plotpath}/overpasses_per_month_and_sat_apr-sep_expatsdomain.png"
  # overpasses_sat_month = f"{plotpath}/overpasses_per_month_and_sat.png"
  mwcch_plt.plot_occurrences_per_month_and_satellite(years, months, satellites, overpasses_sat_month, figsize=(20, 15))

  # plot occurence per year
  overpasses_year = f"{plotpath}/overpasses_per_year_apr-sep_expatsdomain.png"
  # overpasses_year = f"{plotpath}/overpasses_per_year.png"
  mwcch_plt.plot_occurrences_per_year(years, satellites, overpasses_year, figsize=(13, 6))

def count_overpass_occurrences_expats_domain(path, years, months):

  satellites = mwcch_plt.satellite_counter(years, months)

  for y, year in enumerate(years):
    for m, month in enumerate(months):
      
      path_month = f"{path}/{year}/{month:02}"
      files = glob.glob(f"{path_month}/*/*.nc")
      
      if len(files) > 0:
        for f in files:
          sat = mwcch_read.get_sat_from_filepath(f)
          satellites[sat]['count'][y, m] += 1

  return satellites

def plot_times_of_overpasses(datapath, year, month, days, output_name):
  f, axes = plt.subplots(len(days), figsize=(20, 1.8*len(days)))
  f.suptitle("times of overpasses")
  for d in range(len(days)):
    ax = axes[d]
    ax.set_title(f'{year}-{month:02}-{days[d]:02}', y=0.7, x=0.05)
    all_files = match.get_files_in_study_period(datapath, year, month, [days[d]])

    startstamps = []
    for file_path in all_files:
      start, _ = mwcch_read.get_start_and_end_datetimes_from_filepath(file_path)
      startstamps.append(start)

    for t, ts in enumerate(startstamps):
      # ax.axvspan(ts, endstamps[t], ymin=0, ymax=0.5)
      ax.axvline(ts, ymin=0, ymax=0.5)
      # ax.axvline(endstamps[t], ymin=0, ymax=0.5)
    xticks = np.arange(f'{year}-{month:02}-{days[d]:02}T00:00', 
                      f'{year}-{month:02}-{days[d]:02}T23:59', 
                      np.timedelta64(1, 'h'), dtype='datetime64[h]')
    ax.set_xticks(xticks, xticks)#, rotation=20)
    if d < len(days) - 1:
      ax.tick_params(axis='x',          # changes apply to the x-axis
                      which='both',      # both major and minor ticks are affected
                      bottom=True,      # ticks along the bottom edge are off
                      labelbottom=False)

    ax.set_xlim(xticks[0], xticks[-1] + np.timedelta64(1, 'h'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.set_yticks([0, 1], ["", ""])
    ax.set_ylim

    # For the minor ticks, use no labels; default NullFormatter.
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.grid(which="both")

  plt.tight_layout()
  plt.savefig(output_name, bbox_inches='tight')
  plt.close()

# %%
def plot_times_of_overpasses_for_different_years():
  datapath = mwcch_read.MWCCH_PATH
  plotpath = "/net/merisi/pbigalke/plots/data_investigation/MWCC-H_new_in_domain"
  if not os.path.exists(plotpath):
     os.makedirs(plotpath)
  years = np.arange(1999, 2024, 1)
  months = [6]
  days = np.arange(1, 6, 1)

  for year in years:
    for month in months:
      output_name = f"{plotpath}/{year}-{month:02}_times_of_overpasses.png"
      plot_times_of_overpasses(datapath, year, month, days, output_name)


# %%
if __name__ == "__main__":
   plot_times_of_overpasses_for_different_years()
# %%
