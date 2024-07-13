# %%
import xarray as xr
import numpy as np
import glob
import os
import sys
sys.path.append("..")
# import my own script
from config.domain_info import domain_expats
import helpers.helper_conversions as hlp

# %%
channel_info = {
    # scene_img_1:
    "channel_8": {"scene": 'scene_img1', "number": 8, "frequency": "150+-1.2", "polarisation": "h", "intercalibrated": False, "used_for_MWCCH":True}, 
    "channel_9": {"scene": 'scene_img1', "number": 9, "frequency": "183+-6.6", "polarisation": "h", "intercalibrated": False, "used_for_MWCCH":True}, 
    "channel_10": {"scene": 'scene_img1', "number": 10, "frequency": "183+-3.0", "polarisation": "h", "intercalibrated": False, "used_for_MWCCH":True}, 
    "channel_11": {"scene": 'scene_img1', "number": 11, "frequency": "183+-1.0", "polarisation": "h", "intercalibrated": False, "used_for_MWCCH":True}, 
    # scene_img_2:
    "channel_17": {"scene": 'scene_img2', "number": 17, "frequency": "91+-0.9", "polarisation": "v", "intercalibrated": True, "used_for_MWCCH":True}, 
    "channel_18": {"scene": 'scene_img2', "number": 18, "frequency": "91+-0.9", "polarisation": "h", "intercalibrated": True, "used_for_MWCCH":True}, 
    "channel_25": {"scene": 'scene_img2', "number": 25, "frequency": "85", "polarisation": "v", "intercalibrated": False, "used_for_MWCCH":False}, 
    "channel_26": {"scene": 'scene_img2', "number": 26, "frequency": "85", "polarisation": "h", "intercalibrated": False, "used_for_MWCCH":False}, 
}

def _get_scenes(channels):
    scenes = []
    for ch in channels:
        scene = channel_info[ch]["scene"]
        if scene not in scenes:
            scenes.append(scene)
    return scenes

def _read_SSMIS_TB_scene(filepath, scene, dataset=None):

    if dataset is None:
        # extract starting time of each scan from general data
        with xr.open_dataset(filepath) as data_general:
            time_scan = data_general.time

        # open scene data and add starting time of each scan to time coordiniate
        with xr.open_dataset(filepath, group=scene) as data_scene:
            dataset = data_scene[['lon', 'lat', 'tb']].assign_coords(time=('time', time_scan.values))

    else:
        # open scene data and merge to existing dataset
        with xr.open_dataset(filepath, group=scene) as data_scene:
            dataset = dataset.merge(data_scene['tb'], compat='override', join='outer')
    
    return dataset

def _crop_over_domain(data, domain):
    # select only our domain
    mask_domain = (data.lon > domain[0]) & (data.lon < domain[1]) \
        & (data.lat > domain[2]) & (data.lat < domain[3])
    data = data.where(mask_domain, drop=True)
    return data

def _generate_filename_for_overpass(data_overpass):

    date_str = hlp.get_datestring_from_npdatetime(data_overpass.time.values[0])
    starttime_str = hlp.get_timestring_from_npdatetime(data_overpass.time.values[0])
    endtime_str = hlp.get_timestring_from_npdatetime(data_overpass.time.values[-1])
    return f"{date_str}_S{starttime_str}_E{endtime_str}_CMSAF_SSMIS_overpass_expatsdomain"


def crop_data_and_save_overpasses(filepath, scenes, domain, output_path):
    
    # read in all scenes into one dataset
    dataset = None
    for scene in scenes:
        dataset =  _read_SSMIS_TB_scene(filepath, scene, dataset=dataset)

    # crop over domain
    dataset = _crop_over_domain(dataset, domain=domain)

    # split dataset at large time gaps:

    # get differences between remaining timestamps in minutes
    dt = np.diff(dataset.time).astype("timedelta64[ms]").astype(int) / 1000 / 60

    # find indices where difference is larger than 1 hour (--> new overpass)
    indices_timegap = np.argwhere(dt > 10)[:, 0] + 1

    # loop over separate overpasses
    for i in range(len(indices_timegap)+1):
        if i == 0:
            data_overpass = dataset.isel(time=slice(0, indices_timegap[i]))
            filename = _generate_filename_for_overpass(data_overpass)
            data_overpass.to_netcdf(f"{output_path}/{filename}.nc")
            print(f"{output_path}/{filename}.nc")

        elif i == len(indices_timegap):
            data_overpass = dataset.isel(time=slice(indices_timegap[i-1], None))
            filename = _generate_filename_for_overpass(data_overpass)
            data_overpass.to_netcdf(f"{output_path}/{filename}.nc")
            print(f"{output_path}/{filename}.nc")

        else:
            data_overpass = dataset.isel(time=slice(indices_timegap[i-1], indices_timegap[i]))
            filename = _generate_filename_for_overpass(data_overpass)
            data_overpass.to_netcdf(f"{output_path}/{filename}.nc")
            print(f"{output_path}/{filename}.nc")



# %%
path = "/net/merisi/pbigalke/data/CMSAF_SSMIS"
outputpath = "/net/merisi/pbigalke/data/CMSAF_SSMIS_processed/2022/06/05"
if not os.path.exists(outputpath):
    os.makedirs(outputpath)

# example_files = sorted(glob.glob(f"{path}/*.nc"))
example_file = f"{path}/BTRin20220605000000424SSF18E1GL.nc"
channels = [f"channel_{c}" for c in [8, 9, 10, 11, 17, 18]]
scenes = _get_scenes(channels)

crop_data_and_save_overpasses(example_file, scenes, domain_expats, outputpath)



# %%
