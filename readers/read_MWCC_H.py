
# %%
import pandas as pd
from datetime import datetime
import glob


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
    mask_out_of_bounds = (data.lon < domain["minlon"]) | (data.lon > domain["maxlon"]) | \
                (data.lat < domain["minlat"]) | (data.lat > domain["maxlat"])
    index_out_of_bounds = data[mask_out_of_bounds].index
    data.drop(index_out_of_bounds , inplace=True)
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


def read_mwcch_file(file_path, domain=None):
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
    df.columns = _get_column_names(detector)

    if domain is not None:
        # select only over given domain
        df = _crop_over_domain(df, domain)

    # add another column containing datetime
    #df.insert(loc = 0,
    #         column = 'datetime',
    #         value =  df.apply(lambda x : datetime(int(x['year']), int(x['month']), int(x['day']), int(x['hour']), int(x['min']), int(x['sec'])), axis=1))
    return df

def get_y_m_d_from_mwcch_filepath(file_path):
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


def get_mwcch_files_in_study_period(mwcch_directory, detectors, years, months=None, days=None):
    
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
                    year, month, day = get_y_m_d_from_mwcch_filepath(f)
                except ValueError:
                    print("error when retrieving date string from file path: ", f)
                
                if month in months:
                    if day in days:
                        mwcch_files.append(f)

    return mwcch_files

# %%
if __name__ == '__main__':
    import numpy as np
    # test on exaple file
    example_file = "mhs_METOPB_20230724-S1905-E2046_056289"
    satellite = 'METOPB'
    
    path = "/net/merisi/pbigalke/data/MWCC-H"
    years = [2022]
    months = [6]
    days = [5]
    detectors = ["ATMS", "MHS", "SSMIS"]
    all_files = get_mwcch_files_in_study_period(path, detectors, years, months, days)
    print(len(all_files))
    # define domain
    domain = {"minlon":5., "maxlon":16., "minlat":42., "maxlat":51.5}
    for f in all_files:
        print('-----------------------------------------------------')
        print(f)
        data = read_mwcch_file(f, domain=domain)
        if np.sum(data.hail_probability) > 0:
            print(data)
# %%
