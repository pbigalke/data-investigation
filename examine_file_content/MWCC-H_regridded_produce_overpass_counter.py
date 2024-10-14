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

# %%
def count_overpasses_per_year_hour_hailclass_area_and_sat(path, years,
                                                      output_filename="overpasses_per_year_hour_hailclass_covered_area_sat",
                                                      overwrite=False):

  counter_filename = f"{path}/{output_filename}.nc"
  if os.path.exists(counter_filename) and not overwrite:
    print("thingy is here")
    with xr.load_dataset(counter_filename) as counter:
      return counter
  
  else:
    # coords
    hours = np.arange(0, 24, 1)
    hail_classes = mwcch_read.get_hail_class(poh=None, type="number")
    area = np.arange(0, 101, 1)
    sat = mwcch_read.get_satellite()

    # vars
    N_overpasses = np.zeros((len(years), len(hours), len(hail_classes),  len(area), len(sat)))
    
    # create dataset
    count_overpass = xr.Dataset(
      data_vars=dict(
          N_overpasses=(["year", "hour", "hail_class", "area_perc", "sat"], N_overpasses),
          hail_class_names=(["hail_class"], mwcch_read.get_hail_class(type="name")),
      ),
      coords=dict(
          year=("year", years),
          hour=("hour", hours),
          hail_class=("hail_class", hail_classes),
          area_perc=("area_perc", area),
          sat=("sat", sat),
     ),
    )

    # start loop over all folders (years, months, days)
    files_processed = 0
    for year in years:
      for month in np.arange(1, 13, 1):
        for day in np.arange(1, 32, 1):

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

              # get satellite from filename
              sat = mwcch_read.get_satellite(file_path=f)

              try:
                # increase counter at specific sat, year, month, hailclass and area percentage
                count_overpass.N_overpasses.loc[dict(year=year, hour=hour, 
                                                    hail_class=max_hail_class, area_perc=area_perc, 
                                                    sat=sat)] += 1
              except KeyError:
                print("There was a key error (probably due to hail class and nans) in file: ", f)
              
              # count number of processed files
              files_processed += 1

    # print total number of files in this study period
    print("total number of files processed: ", files_processed, flush=True)

    # set non valid datetime to nan
    if year in count_overpass.coords \
      and month in count_overpass.coords \
        and day in count_overpass.coords:
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

def sum_over_dimension_and_save(counter, dim, output_filename):
  # save to file
  print("saving to file: ", output_filename)
  counter.sum(dim=dim).to_netcdf(output_filename)
  return

def load_counter_file(counter_filename):
  if os.path.exists(counter_filename):
    print("thingy is here")
    with xr.load_dataset(counter_filename) as counter:
      return counter
  return None

# %%
def create_smaller_counter_from_larger_one():
  with xr.load_dataset(f"{datapath}/overpasses_per_hour_hailclass_and_covered_area.nc") as counter:
    overpass_area = counter
    # save new file only dependent on hail class, year and area percentage
    output_filename = f"{datapath}/overpasses_per_year_hailclass_area.nc"
    sum_over_dimension_and_save(counter, ["month", "day", "hour"], output_filename)

    # save new file only dependent on hail class and area percentage
    output_filename = f"{datapath}/overpasses_per_hailclass_area.nc"
    sum_over_dimension_and_save(counter, ["year", "month", "day", "hour"], output_filename)

# %%
if __name__ == "__main__":
  years = np.arange(1999, 2024, 1).astype(int)
  count_overpasses_per_year_hour_hailclass_area_and_sat(datapath, years,
                                                      output_filename="overpasses_per_year_hour_hailclass_covered_area_sat",
                                                      overwrite=False)

