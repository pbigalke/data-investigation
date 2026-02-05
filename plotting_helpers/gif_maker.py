"""
Code to read and plot the video of 1 dday radar images of rain rates
"""
import glob
from PIL import Image
import os

def gif_maker(image_files, gif_path, sec_per_frame=1):
    """
    script to create animated gif from a folder containing images

    Args:
        image_files (string): list of paths to png images
        gif_path (string): path for gif file
        gif_duration (int): duration for gif (typical 250)
        
    """
    # read images into image_array
    image_array = []
    for file in image_files:
        image = Image.open(file)
        image_array.append(image)

    im = image_array[0]      
    im.save(gif_path, 
            format='png',
            save_all=True, 
            append_images=image_array, 
            duration=sec_per_frame*100, 
            loop=0)


# def convert_gif_to_mp4(gif_path, mp4_path):
#     clip = VideoFileClip(gif_path)
#     clip.write_videofile(mp4_path, codec='libx264')


def convert_gifs_to_mp4(gif_folder, mp4_folder):
    """
    Converts a GIF files to MP4 format using ffmpeg.
    
    Args:
        gif_folder (str): Path to the input GIF folder.
        mp4_folder (str): Path where the output MP4 files will be saved.
    """
    import os
    import subprocess

    # Root directory containing GIFs
    input_root = gif_folder

    # Directory where MP4s will be saved
    output_root = mp4_folder
    os.makedirs(output_root, exist_ok=True)

    # Output video settings
    output_fps = 10

    for dirpath, _, filenames in os.walk(input_root):
        for filename in filenames:
            if filename.lower().endswith(".gif"):
                gif_path = os.path.join(dirpath, filename)

                # Get relative path from input_root and use it to build output path
                rel_path = os.path.relpath(dirpath, input_root)
                output_dir = os.path.join(output_root, rel_path)
                os.makedirs(output_dir, exist_ok=True)

                mp4_filename = os.path.splitext(filename)[0] + ".mp4"
                mp4_path = os.path.join(output_dir, mp4_filename)

                if os.path.exists(mp4_path):
                    print(f"🔁 Skipping existing MP4: {mp4_path}")
                    continue

                print(f"🎞️ Converting: {gif_path} -> {mp4_path}")

                try:
                    subprocess.run([
                        "ffmpeg",
                        "-y",  # overwrite output if needed
                        "-i", gif_path,
                        "-vf", f"fps={output_fps},pad=ceil(iw/2)*2:ceil(ih/2)*2",  # even dimensions
                        "-c:v", "libx264",
                        "-preset", "slow",         # compression trade-off: slower = smaller file
                        "-crf", "32",
                        "-pix_fmt", "yuv420p",
                        "-movflags", "faststart",
                        mp4_path
                    ], check=True)
                    print(f"✅ Saved MP4: {mp4_path}")
                except subprocess.CalledProcessError as e:
                    print(f"❌ FFmpeg failed for {gif_path}: {e}")
