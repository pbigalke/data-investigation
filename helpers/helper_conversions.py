import pandas as pd

def get_datestring_from_npdatetime(npdatetime):
    
    year = pd.to_datetime(npdatetime).year
    month = pd.to_datetime(npdatetime).month
    day = pd.to_datetime(npdatetime).day

    hour = pd.to_datetime(npdatetime).hour
    minute = pd.to_datetime(npdatetime).minute

    date_string = f"{year:04}{month:02}{day:02}_{hour:02}{minute:02}"
    return date_string