"""
Code to read and plot the video of 1 dday radar images of rain rates
"""
import glob
from PIL import Image
import os

def gif_maker(image_files, gif_name, gif_path, sec_per_frame=1):
    """
    script to create animated gif from a folder containing images

    Args:
        image_files (string): list of paths to png images
        gif_name (string): string as filename for gif
        gif_path (string): path for gif file
        gif_duration (int): duration for gif (typical 250)
        
    """
    # read images into image_array
    image_array = []
    for file in image_files:
        image = Image.open(file)
        image_array.append(image)

    im = image_array[0]      
    im.save(os.path.join(gif_path, f"{gif_name}.gif"), 
            format='png',
            save_all=True, 
            append_images=image_array, 
            duration=sec_per_frame*100, 
            loop=0)
