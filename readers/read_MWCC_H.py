
# %%
import pandas as pd
from datetime import datetime


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
    

def _get_column_names(satellite):
    """ read column names depending on satellite

    Parameters
    ----------
    satellite : string
        satellite that was used

    Returns
    -------
    list(string)
        names of columns in data file - differs for different satellites!! TODO: add other satellites here!
    """
    if satellite == 'METOPB':
        return ['year', 'month', 'day', 'hour', 'minute', 'second', 'lat', 'lon', 'cloud_type', 'TB', 'POH']
    else:
        return None


def read(filename, satellite='METOPB', domain=None):
    """ read MWCC-H output containing probability of hail into dataframe

    Parameters
    ----------
    filename : string or path
        path to file
    satellite : str, optional
        defines from which satellite the POH was calculated, by default 'METOPB' (as it is the only one I have looked at so far)
    domain : dict, optional
        if not None data is cropped to this domain,
        containing "minlon", "maxlon", "minlat", "maxlat", by default None

    Returns
    -------
    pandas dataframe
        MWCC-H output (cropped) as dataframe with column names
    """
    # read file
    df_raw = pd.read_csv(filename, sep='\t', header=None)

    # rearrange the data into proper dataframe
    df = df_raw[0].str.split(expand=True).astype(float)

    # add the names of columns
    df.columns = _get_column_names(satellite)

    if domain is not None:
        # select only over given domain
        df = _crop_over_domain(df, domain)

    # add another column containing datetime
    df.insert(loc = 0,
              column = 'datetime',
              value =  df.apply(lambda x : datetime(int(x['year']), int(x['month']), int(x['day']), int(x['hour']), int(x['minute']), int(x['second'])), axis=1))
    return df


# %%
if __name__ == '__main__':
    # test on exaple file
    example_file = "mhs_METOPB_20230724-S1905-E2046_056289"
    satellite = 'METOPB'
    
    path = "/net/merisi/pbigalke/data/MWCC-H/"
    years = [2022]
    months = [6]

    


    # define domain
    domain = {"minlon":5., "maxlon":16., "minlat":42., "maxlat":51.5}
    data = read(example_file, satellite=satellite, domain=domain)
    print(data)
# %%
