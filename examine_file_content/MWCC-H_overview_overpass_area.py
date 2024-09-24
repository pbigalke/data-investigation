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
import helpers.datetime_helper as hlp
import readers.read_processed_MWCC_H as mwcch_read
import MWCCH_overview_plots as mwcch_plt
from config.domain_info import domain_expats


# %%
def count_overpasses_per_hour_and_area(path, years, months,
                                       output_filename="overpasses_per_hour_and_covered_area",
                                       overwrite=False):

  counter_filename = f"{path}/{output_filename}.nc"
  if os.path.exists(counter_filename) and not overwrite:
    print("thingy is here")
    with xr.load_dataset(counter_filename) as counter:
      return counter
  
  else:
    # coords
    days = np.arange(1, 32, 1)
    hours = np.arange(0, 24, 1)
    area = np.arange(0, 101, 1)
    # vars
    N_overpasses = np.zeros((len(years), len(months), len(days), len(hours), len(area)))
    
    count_overpass = xr.Dataset(
      data_vars=dict(
          N_overpasses=(["year", "month", "day", "hour", "area_perc"], N_overpasses),
      ),
      coords=dict(
          year=("year", years),
          month=("month", months),
          day=("day", days),
          hour=("hour", hours),
          area_perc=("area_perc", area),
      ),
    )

    total_n_files = len(clct.get_files_in_study_period(path, years, months=months))
    print("total number of files: ", total_n_files, flush=True)
    files_processed = 0

    for year in years:
      for month in months:
        for day in days:

          path_day = f"{path}/{year}/{month:02}/{day:02}"
          files = glob.glob(f"{path_day}/*.nc")
          
          if len(files) > 0:
            for f in files:

              if files_processed % 1000 == 0:
                print(f"{files_processed}/{total_n_files}", flush=True)

              # find hour from filename
              _, end_dt = mwcch_read.get_start_and_end_timestrings_from_mwcch_filepath(f)
              hour =  int(end_dt[:2])

              # read in hail probability data
              mwcch_data = mwcch_read.read(f).POH.values

              # get number of nan entries:
              N_nans = np.sum(np.isnan(mwcch_data))

              # get total number of pixels
              N_pixel = mwcch_data.shape[0] * mwcch_data.shape[1]

              # calculate area percentage covered by overpass
              area_perc = round(N_nans / N_pixel * 100)

              # increase counter at specific sat, year, month and area percentage
              count_overpass.N_overpasses.loc[dict(year=year, month=month, day=day, 
                                                  hour=hour, area_perc=area_perc)] += 1
              
              # count number of processed files
              files_processed += 1

    # print total number of files in this study period
    print("total number of files processed: ", files_processed, flush=True)

    # set non valid datetime to nan
    count_overpass = set_nonvalid_datetimes_to_nan(count_overpass)

    # save to file so that we don't need to run this again while creating the plots
    count_overpass.to_netcdf(counter_filename)
    return count_overpass

def set_nonvalid_datetimes_to_nan(count_overpass):
  
  for y in count_overpass.year.values:
    for m in count_overpass.month.values:
      for d in count_overpass.day.values:
        try:
          datetime.datetime(year=y,month=m,day=d)
        except(ValueError):
          count_overpass.N_overpasses.loc[{"year": y, "month": m, "day": d}] = np.NaN
  return count_overpass

# %%
# %%
def barplot_occurrences_per_area_fraction(overpass_area, output_name=None, figsize=(10, 8),
                                          fraction=False, log=False):
  
  f, (ax1, ax2) = plt.subplots(2, 1)
  f.set_figheight(figsize[1])
  f.set_figwidth(figsize[0])
  ax1.set_title("distribution of covered area fraction")
  ax2.set_title("cumulative distribution covered area fraction")

  # get total number of overpasses in dataset
  N_total = overpass_area.N_overpasses.sum().values

  # get number of overpasses per area fraction
  area_counts = overpass_area.N_overpasses.sum(dim=["year", "month", "day", "hour"]).values

  # bar plot of number of overpasses per area fraction
  y = area_counts / N_total * 100 if fraction else area_counts
  x_center = overpass_area.area_perc.values
  ax1.bar(x_center, y, -0.8, color="r", align="center")

  # make cumulative plot
  x_edge = np.concatenate((x_center - 0.5, np.array([x_center[-1] + 0.5])))
  x_cumul = np.repeat(x_edge, 2)
  # get cumulative area counts
  y_cumul = np.concatenate((np.array([0]), 
                            np.repeat(np.cumsum(area_counts), 2), 
                            np.array([0])))
  # get cumulateve area counts backwards
  y_cumul_back = np.concatenate((np.array([0]), 
                                 np.repeat(np.cumsum(area_counts[::-1])[::-1], 2),
                                 np.array([0])))
  # plot
  ax2.plot(x_cumul, y_cumul, color="b", linestyle="--")
  ax2.plot(x_cumul, y_cumul_back, color="b", linestyle="-")

  # format x axes
  ax1.set_xlim(x_center[0]-0.5, x_center[-1] + 0.5)
  ax2.set_xlim(x_edge[0], x_edge[-1])

  # format y axes
  for ax in [ax1, ax2]:
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
datapath = mwcch_read.MWCCH_MSGGRID_PATH
print(datapath)
print(os.path.exists(datapath))

years = np.arange(1999, 2024, 1).astype(int)
months = np.arange(4, 10, 1).astype(int)

# count area fractions covered by overpasses
overpass_area = count_overpasses_per_hour_and_area(datapath, years, months,
                                       output_filename="overpasses_per_hour_and_covered_area",
                                       overwrite=False)


# %%
plotpath = "/net/merisi/pbigalke/plots/data_investigation/MWCC-H_new_in_domain"
if not os.path.exists(plotpath):
    os.makedirs(plotpath)

# plot occurrences of max hail per year and hail class
out = f"{plotpath}/area_covered_by_overpasses.png"
barplot_occurrences_per_area_fraction(overpass_area, output_name=out, figsize=(8, 8),
                                      fraction=False, log=False)
out_log = f"{plotpath}/area_covered_by_overpasses_log.png"
barplot_occurrences_per_area_fraction(overpass_area, output_name=out_log, figsize=(8, 8),
                                      fraction=False, log=True)
out_frac = f"{plotpath}/area_covered_by_overpasses_frac.png"
barplot_occurrences_per_area_fraction(overpass_area, output_name=out_frac, figsize=(8, 8),
                                      fraction=True, log=False)
out_frac_log = f"{plotpath}/area_covered_by_overpasses_frac_log.png"
barplot_occurrences_per_area_fraction(overpass_area, output_name=out_frac_log, figsize=(8, 8),
                                      fraction=True, log=True)


# %%
