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
    area = np.arange(0, 100, 1)
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

              # increase counter at specific sat, year, month and hail_level
              count_overpass.N_overpasses.loc[dict(year=year, month=month, day=day, hour=hour, area_perc=area_perc)] += 1
              
              # count number of processed files
              files_processed += 1

    # print total number of files in this study period
    print("total number of files processed: ", files_processed, flush=True)

    # set non valid datetime to nan
    count_overpass = set_nonvalid_datetimes_to_nan(count_overpass)

    # save to file so that we don't need to run this again while creating the plots
    # count_overpass.to_netcdf(counter_filename)
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
  hail_class_counts = hail_counter.N_max_poh.sum(dim=["sat", "year", "month"]).values

  # add number of events of this hail class to bar plot
  x_center = np.arange(0, len(hail_counter.hail_class), 1)
  y_max = hail_class_counts / N_total * 100 if fraction else hail_class_counts
  ax1.bar(x_center, y_max, -0.8, color="r", align="center")

  # add percentage above max poh bars
  perc_max = hail_class_counts / N_total * 100
  for p, perc in enumerate(perc_max):
    position = 1 if y_max[p] == 0 else y_max[p]
    ax1.text(x_center[p], position, f'{perc:.2f}', fontsize=12, 
              horizontalalignment='center', verticalalignment='bottom')

  # add number of events of this hail class to cumulative bar plot
  x_edge = np.arange(0, len(hail_counter.hail_class)+1, 1)
  x_cumul = np.concatenate((x_edge[:1], np.repeat(x_edge[1:-1], 2), x_edge[-1:]))
  y_cumul = np.repeat(np.cumsum(y_max), 2)
  y_cumul_back = np.repeat(np.cumsum(y_max[::-1])[::-1], 2)
  ax2.plot(x_cumul, y_cumul, color="b", linestyle="--")
  ax2.plot(x_cumul, y_cumul_back, color="b", linestyle="-")

  # format x axes
  ax1.set_xticks(x_center, labels=hail_counter.hail_class.values, rotation=45, ha='right')
  ax1.set_xlim(x_center[0]-0.5, x_center[-1] + 0.5)
  ax2.set_xticks(x_edge, labels=get_hail_class_boundaries())
  ax2.set_xlim(x_edge[0], x_edge[-1])

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
def sum_and_mean_overpasses_per_hour_and_year(overpass_counter, output_name=None, figsize=(14, 7), log=False):
  
  f, (ax1, ax2) = plt.subplots(1, 2)
  f.set_figheight(figsize[1])
  f.set_figwidth(figsize[0])
  ax1.set_title("sum of overpasses per hour and year", y=1.0, pad=5)
  ax2.set_title("mean of overpasses per hour and year", y=1.0, pad=5)

  # get axis arrays
  hours = overpass_counter.hour.values
  years = overpass_counter.year.values

  # # sum of overpasses per hour and year
  overpass_per_hour_and_year = overpass_counter.sum(dim=["month", "day", "hail_class"]).N_overpasses.values
  c = ax1.imshow(overpass_per_hour_and_year, cmap="hot")
  f.colorbar(c, ax=ax1,label="total number of overpasses",fraction=0.046, pad=0.04)

    # sum of overpasses per hour and year
  stacked_per_hour_and_year = overpass_counter.stack(z=("month", "day", "hail_class")).N_overpasses
  mean = stacked_per_hour_and_year.mean(dim="z").values
  years = overpass_counter.year.values
  c = ax2.imshow(mean, cmap="hot")
  f.colorbar(c, ax=ax2,label="mean number of overpasses", fraction=0.046, pad=0.04)

  # format axes
  for ax in [ax1, ax2]:
    ax.set_xticks(hours - 0.5, labels=hours)
    ax.set_xlim(hours[0]-0.5, hours[-1]+0.5)
    ax.set_yticks(np.arange(0, len(years))-0.5, labels=years)
    ax.set_ylim(-0.5, len(years)-0.5)
    ax.set_xlabel("hour of the day")
    ax.set_ylabel("years")
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

def daily_mean_overpasses_per_year(overpass_counter, output_name=None, figsize=(14, 7)):
  
  f, ax = plt.subplots(1)
  f.set_figheight(figsize[1])
  f.set_figwidth(figsize[0])
  ax.set_title("mean daily overpasses", y=1.0, pad=5)

  # get axis arrays
  years = overpass_counter.year.values

  # plot mean and std daily overpasses per year
  daily = overpass_counter.sum(dim=("hour", "hail_class")).stack(z=("month", "day")).N_overpasses
  ax.boxplot(daily.transpose(), positions=years)

  # format axes
  ax.set_ylabel("daily # of overpasses")
  ax.set_yticks(np.arange(0, 26, 2))
  ax.set_ylim(0, 25)
  ax.set_xticks(years, labels=years)
  ax.set_xlim(years[0]-0.5, years[-1]+0.5)
  ax.set_xlabel("years")
  ax.grid()

  plt.tight_layout()

  if output_name is not None:
    plt.savefig(output_name, bbox_inches='tight')
    plt.close()
  else:
    plt.show()
    plt.close()

def overpasses_per_daytime_and_hail_class(overpass_counter, hour_interval=1, year=None, output_name=None, figsize=(10, 10), log=False):
  
  f, (ax1, ax2, ax3) = plt.subplots(3)
  f.set_figheight(figsize[1])
  f.set_figwidth(figsize[0])
  ax1.set_title(f"mean number of overpasses each {hour_interval} hour(s)", y=1.0, pad=5)
  ax2.set_title(f"total number of overpasses each {hour_interval} hour(s)", y=1.0, pad=5)
  ax3.set_title(f"frequency of hail classes each {hour_interval} hour(s)", y=1.0, pad=5)

  # get hours of intervals
  hours_all = overpass_counter.hour.values
  hours = hours_all[int(hour_interval/2)::hour_interval]

  # barplot positions and widths to be centered within intervals
  bar_positions = hours+(hour_interval % 2) / 2.
  bar_widths = hour_interval * 0.9

  # roll dataset along the hours with given interval width
  if year is None:
    overpass_interval = overpass_counter.rolling(hour=hour_interval, center=True).sum()
    stack_dim = ("year", "month", "day", "hail_class")
    sum_dim = ["month", "day", "year"]
  else:
    overpass_interval = overpass_counter.sel(year=year).rolling(hour=hour_interval, center=True).sum()
    stack_dim = ("month", "day", "hail_class")
    sum_dim = ["month", "day"]

  # sum of overpasses per hour
  stacked_per_hour = overpass_interval.stack(z=stack_dim).N_overpasses
  mean = stacked_per_hour.mean(dim=("z"))
  ax1.bar(bar_positions, mean.values[int(hour_interval/2)::hour_interval], bar_widths, align="center")
    
  # format axis 1
  ax1.set_ylabel("mean # of overpasses")

  # total number of overpasses
  overpass_per_interval_and_hail_class = overpass_interval.sum(dim=sum_dim).N_overpasses

  # loop over hail classes and 
  bottom = np.zeros(len(hours))
  for h in overpass_per_interval_and_hail_class.hail_class.values:
    hail_class_overpasses = \
      overpass_per_interval_and_hail_class.sel(hail_class=h).values[int(hour_interval/2)::hour_interval]
    ax2.bar(bar_positions, hail_class_overpasses, bar_widths, bottom=bottom, 
            color=hail_class_colors2[h], align="center", label=h)
    bottom += hail_class_overpasses
    
  # format axis 1
  ax2.set_ylabel("# of files")
  ax2.legend(loc=0)

  # frequency of hail classes per hour
  frequ_hail_classes = overpass_per_interval_and_hail_class / overpass_per_interval_and_hail_class.sum(dim="hail_class")

  # loop over hail classes and 
  for h in frequ_hail_classes.hail_class.values:
    if h == "no_hail":
      continue
    hail_class_frequ = frequ_hail_classes.sel(hail_class=h).values[int(hour_interval/2)::hour_interval]
    ax3.plot(hours, hail_class_frequ,color=hail_class_colors2[h], label=h)
    
  # format axis 1
  ax3.set_ylabel("fraction of occurrence")
  ax3.legend(loc=0)

  # format all x axes
  for ax in [ax1, ax2, ax3]:
    ax.set_xticks(hours_all, labels=hours_all)
    ax.set_xlim(hours_all[0], hours_all[-1]+1)
    ax.set_xlabel("hour of the day")
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

plotpath = "/net/merisi/pbigalke/plots/data_investigation/MWCC-H_new_in_domain"
if not os.path.exists(plotpath):
    os.makedirs(plotpath)
years = np.arange(1999, 2024, 1).astype(int)
months = np.arange(4, 10, 1).astype(int)
all_files = clct.get_files_in_study_period(datapath, years, months)
print(len(all_files))

overpass_area = count_overpasses_per_hour_and_area(datapath, years, months,
                                       output_filename="overpasses_per_hour_and_covered_area",
                                       overwrite=True)


# %%
