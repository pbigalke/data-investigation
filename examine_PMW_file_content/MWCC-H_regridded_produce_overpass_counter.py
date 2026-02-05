# This script generates counter files containing the number of overpasses for each year, month, day, hour, 
# hail class and area percentage in the dataset.
# %%
import glob
import xarray as xr
import numpy as np
import datetime
import os
import sys
sys.path.append("..")
import readers.read_processed_MWCC_H as mwcch_read

datapath = mwcch_read.MWCCH_MSGGRID_PATH

# %%
def count_overpasses_per_year_hour_hailclass_area_and_sat(path, years,
                                                      output_filename="overpasses_per_year_hour_hailclass_covered_area_sat",
                                                      overwrite=False):
  """
  Counts the number of overpasses for each satellite, year, hour, hail class and area percentage in the dataset.
  :param path: path to the dataset
  :param years: list of years to count the overpasses for
  :param output_filename: name of the output file to save the counter, if None the counter is returned as an xarray dataset
  :param overwrite: if True, the counter is calculated and saved to file even if the output file already exists, 
                    if False, the counter is loaded from file if it exists, otherwise it is calculated and saved to file
  """
  counter_filename = f"{path}/statistics/{output_filename}.nc"
  if os.path.exists(counter_filename) and not overwrite:
    print("thingy is here")
    with xr.load_dataset(counter_filename) as counter:
      return counter
  
  else:
    # coords
    hours = np.arange(0, 24, 1)
    hail_classes = mwcch_read.get_hail_classes(type="number")
    hail_class_names = mwcch_read.get_hail_classes(type="name")
    area = np.arange(0, 101, 1)
    sat = mwcch_read.get_satellite()

    # vars
    N_overpasses = np.zeros((len(years), len(hours), len(hail_classes),  len(area), len(sat)))
    
    # create dataset
    count_overpass = xr.Dataset(
      data_vars=dict(
          N_overpasses=(["year", "hour", "hail_class", "area_perc", "sat"], N_overpasses),
          hail_class_names=(["hail_class"], hail_class_names),
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
              mwcch_data = mwcch_read.read(f, variables=["hail_class"]).hail_class.values

              # get maximum hail class within this overpass
              max_hail_class = mwcch_read.max_hail_class(mwcch_data, min_pixel=1)

              # calculate area percentage covered by overpass
              area_perc = mwcch_read.area_percentage_covered_by_overpass(mwcch_data)

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

def count_overpasses_per_hour_hailclass_and_area(path, years, months,
                                                output_filename="overpasses_per_hour_hailclass_and_covered_area",
                                                overwrite=False):
  """
  Counts the number of overpasses for each year, month, day, hour, hail class and area percentage in the dataset.
  :param path: path to the dataset
  :param years: list of years to count the overpasses for
  :param months: list of months to count the overpasses for
  :param output_filename: name of the output file to save the counter, if None the counter is returned as an xarray dataset
  :param overwrite: if True, the counter is calculated and saved to file even if the output file already exists, 
                    if False, the counter is loaded from file if it exists, otherwise it is calculated and saved to file
  """
  counter_filename = f"{path}/statistics/{output_filename}.nc"
  if os.path.exists(counter_filename) and not overwrite:
    print("thingy is here")
    with xr.load_dataset(counter_filename) as counter:
      return counter
  
  else:
    # coords
    days = np.arange(1, 32, 1)
    hours = np.arange(0, 24, 1)
    hail_classes = mwcch_read.get_hail_classes(type="number")
    hail_class_names = mwcch_read.get_hail_classes(type="name")
    area = np.arange(0, 101, 1)

    # vars
    N_overpasses = np.zeros((len(years), len(months), len(days), len(hours), len(hail_classes), len(area)))
    
    # create dataset
    count_overpass = xr.Dataset(
      data_vars=dict(
          N_overpasses=(["year", "month", "day", "hour", "hail_class", "area_perc"], N_overpasses),
          hail_class_names=(["hail_class"], hail_class_names),
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
              mwcch_data = mwcch_read.read(f, variables=["hail_class"]).hail_class.values

              # get maximum hail class within this overpass
              max_hail_class = mwcch_read.max_hail_class(mwcch_data, min_pixel=1)

              # calculate area percentage covered by overpass
              area_perc = mwcch_read.area_percentage_covered_by_overpass(mwcch_data)

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
    if year in count_overpass.coords \
      and month in count_overpass.coords \
        and day in count_overpass.coords:
      count_overpass = set_nonvalid_datetimes_to_nan(count_overpass)

    # save to file so that we don't need to run this again while creating the plots
    count_overpass.to_netcdf(counter_filename)
    return count_overpass

def count_overpasses_per_year_hailclass_minpix_and_area(path, years, 
                                                output_filename="overpasses_per_year_hailclass_minpix_and_covered_area",
                                                overwrite=False):
  """
  Counts the number of overpasses for each year, hail class, min pixel and area percentage in the dataset.
  :param path: path to the dataset
  :param years: list of years to count the overpasses for
  :param output_filename: name of the output file to save the counter, if None the counter is returned as an xarray dataset
  :param overwrite: if True, the counter is calculated and saved to file even if the output file already exists, 
                    if False, the counter is loaded from file if it exists, otherwise it is calculated and saved to file
  """
  counter_filename = f"{path}/statistics/{output_filename}.nc"
  if os.path.exists(counter_filename) and not overwrite:
    print("thingy is here")
    with xr.load_dataset(counter_filename) as counter:
      return counter
  
  else:
    # coords
    hail_classes = mwcch_read.get_hail_classes(type="number")
    hail_class_names = mwcch_read.get_hail_classes(type="name")
    min_pixels = np.arange(1, 20, 1)
    area = np.arange(0, 101, 1)

    # vars
    N_overpasses = np.zeros((len(years), len(hail_classes), len(min_pixels), len(area)))
    
    # create dataset
    count_overpass = xr.Dataset(
      data_vars=dict(
          N_overpasses=(["year", "hail_class", "min_pixel", "area_perc"], N_overpasses),
          hail_class_names=(["hail_class"], hail_class_names),
      ),
      coords=dict(
          year=("year", years),
          hail_class=("hail_class", hail_classes),
          min_pixel=("min_pixel", min_pixels),
          area_perc=("area_perc", area),
     ),
    )

    # start loop over all folders (years, months, days)
    files_processed = 0
    for year in years:
      for month in np.arange(4, 10, 1):

        path_month = f"{path}/{year}/{month:02}"
        files = sorted(glob.glob(f"{path_month}/*/*.nc"))
        
        if len(files) > 0:
          for f in files:
            
            if files_processed % 1000 == 0:
              print(f"{files_processed}", flush=True)

            # read in hail class data
            mwcch_data = mwcch_read.read(f, variables=["hail_class"]).hail_class.values

            # calculate area percentage covered by overpass
            area_perc = mwcch_read.area_percentage_covered_by_overpass(mwcch_data)

            # loop over different min pixels
            for minpix in min_pixels:

              # get maximum hail class within this overpass
              max_hail_class = mwcch_read.max_hail_class(mwcch_data, min_pixel=minpix)

              try:
                # increase counter at specific sat, year, month, hailclass and area percentage
                count_overpass.N_overpasses.loc[dict(year=year, hail_class=max_hail_class, min_pixel=minpix, area_perc=area_perc)] += 1
              except KeyError:
                print("There was a key error (probably due to hail class and nans) in file: ", f)
              
            # count number of processed files
            files_processed += 1

    # print total number of files in this study period
    print("total number of files processed: ", files_processed, flush=True)

    # save to file so that we don't need to run this again while creating the plots
    count_overpass.to_netcdf(counter_filename)
    return count_overpass

def set_nonvalid_datetimes_to_nan(count_overpass):
  """
  Sets the number of overpasses to nan for non valid datetimes (e.g. 30th of February) in the counter dataset.
  :param count_overpass: xarray dataset containing the counter of overpasses with dimensions year, month and day
  :return: xarray dataset with non valid datetimes set to nan
  """
  for y in count_overpass.year.values:
    for m in count_overpass.month.values:
      for d in count_overpass.day.values:
        try:
          datetime.datetime(year=y,month=m,day=d)
        except(ValueError):
          count_overpass.N_overpasses.loc[{"year": y, "month": m, "day": d}] = np.NaN
  return count_overpass

def sum_over_dimension_and_save(counter, dim, output_filename):
  """
  Sums the counter over the specified dimension and saves the result to a new file.
  :param counter: xarray dataset containing the counter of overpasses
  :param dim: list of dimensions to sum over
  :param output_filename: name of the output file to save the summed counter, if None the summed counter is returned as an xarray dataset
  """
  # save to file
  print("saving to file: ", output_filename)
  counter.sum(dim=dim).to_netcdf(output_filename)
  return

def load_counter_file(counter_filename):
  """
  Loads the counter file if it exists, otherwise returns None.
  :param counter_filename: name of the counter file to load
  """
  if os.path.exists(counter_filename):
    print("thingy is here")
    with xr.load_dataset(counter_filename) as counter:
      return counter
  return None

# %%
def create_smaller_counter_from_larger_one():
  """
  Creates smaller counter files by summing the larger counter file over the specified dimensions.
  """
  with xr.load_dataset(f"{datapath}/statistics/overpasses_per_hour_hailclass_and_covered_area.nc") as counter:

    # save new file only dependent on hail class, year and area percentage
    output_filename = f"{datapath}/statistics/overpasses_per_year_hailclass_area.nc"
    sum_over_dimension_and_save(counter, ["month", "day", "hour"], output_filename)

    # save new file only dependent on hail class and area percentage
    output_filename = f"{datapath}/statistics/overpasses_per_hailclass_area.nc"
    sum_over_dimension_and_save(counter, ["year", "month", "day", "hour"], output_filename)

# %%
if __name__ == "__main__":
  years = np.arange(1999, 2024, 1).astype(int)
  months = np.arange(4, 10, 1).astype(int)

  # print("counting overpasses per year, hail class, min_pixel and area percentage")
  count_overpasses_per_year_hailclass_minpix_and_area(datapath, years, 
                                                output_filename="overpasses_per_year_hailclass_minpix_and_covered_area",
                                                overwrite=False)

  # print("counting overpasses per year, hour, hail class, area percentage and satellite")
  # count_overpasses_per_year_hour_hailclass_area_and_sat(datapath, years,
  #                                                     output_filename="overpasses_per_year_hour_hailclass_covered_area_sat",
  #                                                     overwrite=True)
  
  # print("counting overpasses per hour, hail class and area percentage")
  # count_overpasses_per_hour_hailclass_and_area(datapath, years, months,
  #                                             output_filename="overpasses_per_hour_hailclass_and_covered_area",
  #                                             overwrite=True)
  
  # print("creating smaller counter files")
  # create_smaller_counter_from_larger_one()


# %%
