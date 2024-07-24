# %%
import os
import glob
import xarray as xr
import pandas as pd
import sys
sys.path.append("..")
# import my own script
import helpers.helper_conversions as hlp
from config.domain_info import domain_expats

# %%
def main():
    path = "/net/merisi/pbigalke/data/MWCC-H/H2MED_data"
    output_path = "/net/merisi/pbigalke/data/MWCC-H/netcdf"
    # years = [2022]
    # months = [6]
    # days = [5]
    # detectors = ["ATMS", "MHS", "SSMIS", "GMI"]
    # all_files = _get_mwcch_files_in_study_period(path, detectors, years, months, days)
    # print(len(all_files))
    # count = 0

    # read all files in directory
    all_files = sorted(glob.glob(f"{path}/*/*/*.asc.gz"))

    count = 0
    count_in_domain = 0
    # loop over files
    for f, fl in enumerate(all_files):

        # print status every few files
        if f % 1000 == 0:
            print(f"{count}/{len(all_files)}: {count_in_domain} files within domain", flush=True)

        if save_mwcch_over_domain_as_netcdf(fl, domain_expats, output_path):
            count_in_domain += 1

        count += 1

#%%
def save_mwcch_over_domain_as_netcdf(mwcch_file, domain, output_path=None):
    
    # read in data file
    data = _read_mwcch_file(mwcch_file, domain=domain)

    if len(data) > 0:
        # get start and end datetime
        start_dt, end_dt = data['datetime'].agg(['min', 'max'])

        # get detector from filename
        detector = _get_detector_from_mwcch_filepath(mwcch_file)

        # get satellite name from filename
        satellite = _get_satellite_from_mwcch_filepath(mwcch_file)

        # get date string from start datetime
        date_string = hlp.get_datestring_from_npdatetime(start_dt)

        # get starting and end time within our domain
        start_time = f"S{hlp.get_timestring_from_npdatetime(start_dt)}"
        end_time = f"E{hlp.get_timestring_from_npdatetime(end_dt)}"
        
        if output_path is not None:
            # define netcdf file name
            netcdf_path = f"{output_path}/{date_string[:4]}/{date_string[4:6]}/{date_string[6:]}"
            if not os.path.exists(netcdf_path):
                os.makedirs(netcdf_path)
            netcdf_file = f"{netcdf_path}/{date_string}_{start_time}_{end_time}_{detector}_{satellite}.nc"

            # save as netcdf file
            data_xr = xr.Dataset.from_dataframe(data)
            data_xr.to_netcdf(netcdf_file)
            print(f"saved to {netcdf_file}")
        return True
    return False


# %%
def _crop_over_domain(data, domain):
    """ crops data over given domain

    Parameters
    ----------
    data : pandas dataframe
        MWCC-H output after conversion into dataframe
    domain : dict
        containing "minlon", "maxlon", "minlat", "maxlat"

    Returns
    -------
    pandas dataframe
        MWCC-H output cropped over domain
    """
    # select only our domain
    mask_out_of_bounds = (data.lon < domain[0]) | (data.lon > domain[1]) | \
                (data.lat < domain[2]) | (data.lat > domain[3])
    index_out_of_bounds = data[mask_out_of_bounds].index
    data.drop(index_out_of_bounds, inplace=True)
    return data
    
def _get_column_names(detector):
    """ read column names depending on satellite

    Parameters
    ----------
    detector : string
        detector that was used

    Returns
    -------
    list(string)
        names of columns in data file - differs for different satellites!! TODO: add other satellites here!
    """
    if detector == "ATMS":
        return ['scan', 'fov', 'year', 'month', 'day', 'hour', 'min', 'sec', 'lat', 'lon', 'cloud_type', 'tb_165', 'POH']
    
    elif detector == "GMI":
        return ['scan', 'fov', 'lat', 'lon', 'tb_89h', 'tb_166v', 'tb_166h', 'tb_186v', 'tb_186h', 'POH']
    
    elif detector == "MHS":
        return ['scan', 'fov', 'year', 'month', 'day', 'hour', 'min', 'sec', 'lat', 'lon', 'rr', 'flag1', 'flag2', 'flag3', 'flag4', 'POH']
    
    elif detector == "SSMIS":
        return ['year', 'month', 'day', 'hour', 'min', 'sec', 'lat', 'lon', 'cloud_type', 'tb_150', 'POH']

def _read_mwcch_file_old(file_path, domain=None):
    """ read MWCC-H output containing probability of hail into dataframe

    Parameters
    ----------
    filename : string or path
        path to file
    domain : dict, optional
        if not None data is cropped to this domain,
        containing "minlon", "maxlon", "minlat", "maxlat", by default None

    Returns
    -------
    pandas dataframe
        MWCC-H output (cropped) as dataframe with column names
    """
    # read detector name from file_path
    detector = file_path.split('/')[-2]
    
    # read file
    df_raw = pd.read_csv(file_path, sep='\t', header=None)

    # rearrange the data into proper dataframe
    df = df_raw[0].str.split(expand=True).astype(float)

    # add the names of columns
    df.columns = _get_column_names()

    if domain is not None:
        # select only over given domain
        df = _crop_over_domain(df, domain)

    # add another column containing datetime
    #df.insert(loc = 0,
    #         column = 'datetime',
    #         value =  df.apply(lambda x : datetime(int(x['year']), int(x['month']), int(x['day']), int(x['hour']), int(x['min']), int(x['sec'])), axis=1))
    return df

def _read_mwcch_file(file_path, domain=None):
    """ read MWCC-H output containing probability of hail into dataframe

    Parameters
    ----------
    filename : string or path
        path to file
    domain : dict, optional
        if not None data is cropped to this domain,
        containing "minlon", "maxlon", "minlat", "maxlat", by default None

    Returns
    -------
    pandas dataframe
        MWCC-H output (cropped) as dataframe with column names
    """
    # read file
    df_raw = pd.read_csv(file_path, sep='\t', header=None)

    # rearrange the data into proper dataframe
    df = df_raw[0].str.split(expand=True).astype(float)
    
    # add the names of columns
    df.columns = ['year', 'month', 'day', 'hour', 'minute', 'second', 'lat', 'lon', 'cloud_type', 'TB', 'POH']

    if domain is not None:
        # select only over given domain
        df = _crop_over_domain(df, domain)

    # add another column containing datetime
    df['datetime'] = pd.to_datetime(df[['year', 'month', 'day', 'hour', 'minute', 'second']])

    # sort new and leave out unnecessary date and time columns
    df = df[ ['datetime'] + ['lat'] + ['lon'] + ['cloud_type'] + ['TB'] + ['POH'] ]
    
    return df

def _get_y_m_d_from_mwcch_filepath(file_path):
    # get year from path
    year = file_path.split('/')[-3]

    file_name = file_path.split('/')[-1]    

    # find index of year-substring in filename
    idx_date = file_name.find(year)

    # extract date from filename
    year = int(file_name[idx_date:idx_date+4])
    month = int(file_name[idx_date+4:idx_date+6])
    day = int(file_name[idx_date+6:idx_date+8])

    return year, month, day

def _get_satellite_from_mwcch_filepath(file_path):
    satellites = ['meto01', 'meto02', 'meto03', 'noaa15', 'noaa16', 'noaa17', 'noaa18', 'noaa19', 
                  'n20', 'n21', 'npp', 'f16', 'f17', 'gpm']
    for sat in satellites:
        if sat in file_path.lower():
            return sat
    return None

def _get_detector_from_mwcch_filepath(file_path):
    return file_path.split('/')[-2]

def _get_mwcch_files_in_study_period(mwcch_directory, detectors, years, months=None, days=None):
    
    if detectors is not None and not isinstance(detectors, list):
        detectors = list(detectors)
    if years is not None and not isinstance(years, list):
        years = list(years)
    if months is not None and not isinstance(months, list):
        months = list(months)
    if days is not None and not isinstance(days, list):
        days = list(days)

    mwcch_files = []

    for year in years:
        for detector in detectors:
            for f in glob.glob(f"{mwcch_directory}/{year}/{detector}/*.asc.gz"):
                #mwcch_files.append(f)
                try:
                    year, month, day = _get_y_m_d_from_mwcch_filepath(f)
                except ValueError:
                    print("error when retrieving date string from file path: ", f)
                
                if month in months:
                    if day in days:
                        mwcch_files.append(f)

    return mwcch_files

# %%
if __name__ == "__main__":
    # main()
    path = "/net/merisi/pbigalke/data/MWCC-H/H2MED_data"
    outpath = "/net/merisi/pbigalke/data/MWCC-H/netcdf"
    years = [2022]
    months = [6]
    days = [5]
    detectors = ["ATMS", "MHS", "SSMIS", "GMI"]
    all_files = _get_mwcch_files_in_study_period(path, detectors, years, months, days)
    for f in all_files:
        if save_mwcch_over_domain_as_netcdf(f, domain_expats, output_path=outpath):
            print(os.path.basename(f))

# %%
