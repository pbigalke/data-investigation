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
import plotting.plot_MWCC_H as mwcch_plt
from config.domain_info import domain_expats


# %%
def count_overpasses_per_hour_hailclass_and_area(path, years, months,
                                                 output_filename="overpasses_per_hour_hailclass_and_covered_area",
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
    hail_classes = mwcch_read.get_hail_class(poh=None, type="number")
    area = np.arange(0, 101, 1)

    # vars
    N_overpasses = np.zeros((len(years), len(months), len(days), len(hours), len(hail_classes),  len(area)))
    
    # create dataset
    count_overpass = xr.Dataset(
      data_vars=dict(
          N_overpasses=(["year", "month", "day", "hour", "hail_class", "area_perc"], N_overpasses),
      ),
      coords=dict(
          year=("year", years),
          month=("month", months),
          day=("day", days),
          hour=("hour", hours),
          hail_class=("hail_class", hail_classes),
          area_perc=("area_perc", area),
      ),
    )
    
    # Add a description to the 'hail_class' coordinate explaining meaning of the classes
    hail_classes_names = mwcch_read.get_hail_class(poh=None, type="name")
    description = "hail classes are defined as follows: "
    for h in hail_classes:
        description += f"\n{h}: {hail_classes_names[h]}"
    count_overpass['hail_class'].attrs['description'] = description

    # start loop over all folders (years, months, days)
    files_processed = 0
    for year in years:
      for month in months:
        for day in days:

          path_day = f"{path}/{year}/{month:02}/{day:02}"
          files = glob.glob(f"{path_day}/*.nc")
          
          if len(files) > 0:
            for f in files:

              if files_processed % 1000 == 0:
                print(f"{files_processed}", flush=True)

              # find hour from filename
              _, end_dt = mwcch_read.get_start_and_end_timestrings_from_mwcch_filepath(f)
              hour =  int(end_dt[:2])

              # read in hail probability data
              mwcch_data = mwcch_read.read(f).hail_class.values

              # get maximum hail class within this overpass
              max_hail_class = 0 if np.isnan(np.nanmax(mwcch_data)) else np.nanmax(mwcch_data)

              # get number of nan entries:
              N_nans = np.sum(np.isnan(mwcch_data))
              # get total number of pixels
              N_pixel = mwcch_data.shape[0] * mwcch_data.shape[1]
              # calculate area percentage covered by overpass
              area_perc = round(N_nans / N_pixel * 100)
              try:
                # increase counter at specific sat, year, month, hailclass and area percentage
                count_overpass.N_overpasses.loc[dict(year=year, month=month, day=day, hour=hour, 
                                                    hail_class=max_hail_class, area_perc=area_perc)] += 1
              except KeyError:
                print("There was a key error (probably due to hail class and nans) in file: ", f)
              
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
def barplot_occurrences_per_area_fraction(overpass_area, output_name=None, figsize=(10, 8),
                                          fraction=False, log=False):
  
  f, ax = plt.subplots(1)
  f.set_figheight(figsize[1])
  f.set_figwidth(figsize[0])
  ax.set_title("distribution of covered area fraction")

  # get total number of overpasses in dataset
  N_total = overpass_area.N_overpasses.sum().values

  # get number of overpasses per area fraction and hail_class
  area_hail_counts = overpass_area.N_overpasses.sum(dim=["year", "month", "day", "hour"])

  # get hail class names
  hail_class_names = mwcch_read.get_hail_class(poh=None, type="name")

  # define bottom of barplots
  bottom = np.zeros(area_hail_counts.area_perc.shape)

  # loop over hail classes and fill in barplots
  for h in overpass_area.hail_class.values:

    # get counts only for this hail_class
    area_counts = area_hail_counts.sel(hail_class=h).values

    # get color of hail_class
    color = mwcch_plt.hail_class_colors_list[int(h)]

    # bar plot of number of overpasses per area fraction
    y = area_counts / N_total * 100 if fraction else area_counts
    x_center = overpass_area.area_perc.values
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

def plot_occurrences_per_hail_class(overpass_area, area_threshold=0, output_name=None, 
                                    figsize=(15, 5), fraction=False, only_hail=False):
  
  f, (ax1, ax2) = plt.subplots(1, 2, width_ratios=[1,2])
  f.set_figheight(figsize[1])
  f.set_figwidth(figsize[0])
  ax1.set_title("distribution of hail classes")
  ax2.set_title("hail classes over the years")

  # select only overpasses with certain area threshold and sum over all areas
  area_filtered_data = overpass_area.where(overpass_area['area_perc'] >= area_threshold, drop=True)

  # get number of overpasses per year and hail_class
  yearly_hail_counts = area_filtered_data.N_overpasses.sum(dim=["month", "day", "hour", "area_perc"])

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
datapath = mwcch_read.MWCCH_MSGGRID_PATH
years = np.arange(1999, 2024, 1).astype(int)
months = np.arange(4, 10, 1).astype(int)

# count area fractions covered by overpasses
overpass_area = count_overpasses_per_hour_hailclass_and_area(datapath, years, months, 
                                                             output_filename="overpasses_per_hour_hailclass_and_covered_area",
                                                             overwrite=False)

# %%
# plot the distribution of hail classes per year and in total
plotpath = "/net/merisi/pbigalke/plots/data_investigation/MWCC-H_hail_occurrence"
if not os.path.exists(plotpath):
    os.makedirs(plotpath)
# loop over different thresholds
for t in [0, 10, 20, 30, 40]:

  out = f"{plotpath}/hail_class_distribution_development_areathresh{t}.png"
  plot_occurrences_per_hail_class(overpass_area, area_threshold=t, output_name=out)

  out_only_hail = f"{plotpath}/hail_class_distribution_development_areathresh{t}_onlyhail.png"
  plot_occurrences_per_hail_class(overpass_area, area_threshold=t, output_name=out_only_hail, only_hail=True)

# %%
# plot the distribution of area covered by the overpasses


plotpath = "/net/merisi/pbigalke/plots/data_investigation/MWCC-H_new_in_domain"
if not os.path.exists(plotpath):
    os.makedirs(plotpath)

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
