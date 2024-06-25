import xarray as xr
import numpy as np
import glob
import os

# %%
channel_info = {
    # scene_img_1:
    "channel_8": {"scene": 'scene_img1', "frequency": "150+-1.2", "polarisation": "h", "intercalibrated": False, "used_for_MWCCH":True}, 
    "channel_9": {"scene": 'scene_img1', "frequency": "183+-6.6", "polarisation": "h", "intercalibrated": False, "used_for_MWCCH":True}, 
    "channel_10": {"scene": 'scene_img1', "frequency": "183+-3.0", "polarisation": "h", "intercalibrated": False, "used_for_MWCCH":True}, 
    "channel_11": {"scene": 'scene_img1', "frequency": "183+-1.0", "polarisation": "h", "intercalibrated": False, "used_for_MWCCH":True}, 
    # scene_img_2:
    "channel_17": {"scene": 'scene_img2', "frequency": "91+-0.9", "polarisation": "v", "intercalibrated": True, "used_for_MWCCH":True}, 
    "channel_18": {"scene": 'scene_img2', "frequency": "91+-0.9", "polarisation": "h", "intercalibrated": True, "used_for_MWCCH":True}, 
    "channel_25": {"scene": 'scene_img2', "frequency": "85", "polarisation": "v", "intercalibrated": False, "used_for_MWCCH":False}, 
    "channel_26": {"scene": 'scene_img2', "frequency": "85", "polarisation": "h", "intercalibrated": False, "used_for_MWCCH":False}, 
}

