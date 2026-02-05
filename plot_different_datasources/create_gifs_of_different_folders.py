# Script to create gifs from different folders of images. 
# The gifs are created with the helper function gif_maker in plotting_helpers/gif_maker.py.
# %% 
import os
import glob
import sys
sys.path.append("..")
from plotting_helpers.gif_maker import gif_maker

def main():
    gif_path = "/net/merisi/pbigalke/plots/data_investigation/case_study_20220605/gifs"
    if not os.path.exists(gif_path):
        os.makedirs(gif_path)

    # MSG rapid scan with color
    # msg_rapidscan_colors = "/net/merisi/pbigalke/plots/data_investigation/case_study_20220605/MSG_rapidscan/color_masked"
    # msg_rapidscan_colors_imgs = sorted(glob.glob(os.path.join(msg_rapidscan_colors, '*.png')))
    # print("making a gif from: ")
    # print(msg_rapidscan_colors)
    # gif_maker(msg_rapidscan_colors, '20220605_MSG_rapidscan_colored', gif_path, 1)

    # MSG rapid scan greyscale full color range
    # msg_rapidscan_grey = "/net/merisi/pbigalke/plots/data_investigation/case_study_20220605/MSG_rapidscan/german_domain"
    # msg_rapidscan_grey_imgs = sorted(glob.glob(os.path.join(msg_rapidscan_grey, '*.png')))
    # print("making a gif from: ")
    # print(msg_rapidscan_grey)
    # gif_maker(msg_rapidscan_grey, '20220605_MSG_rapidscan_grey', gif_path, 1)

    # MSG rapid scan greyscale min200_max280
    # msg_rapidscan_min200_max280 = "/net/merisi/pbigalke/plots/data_investigation/case_study_20220605/MSG_rapidscan/min200_max280"
    # msg_rapidscan_min200_max280_imgs = sorted(glob.glob(os.path.join(msg_rapidscan_min200_max280, '*.png')))
    # print("making a gif from: ")
    # print(msg_rapidscan_min200_max280)
    # gif_maker(msg_rapidscan_min200_max280, '20220605_MSG_rapidscan_min200_max280', gif_path, 1)

    # # MSG plus hail probability
    # mwcch_MSG = "/net/merisi/pbigalke/plots/data_investigation/case_study_20220605/MSG_MWCCH_rapidscan/min200_max280"
    # mwcch_MSG_imgs = sorted(glob.glob(os.path.join(mwcch_MSG, '*.png')))
    # print("making a gif from: ")
    # print(mwcch_MSG_imgs)
    # gif_maker(mwcch_MSG_imgs, f'20220605_mwcch_msg', gif_path, sec_per_frame=5)

    mwcch_gif_path = os.path.join(gif_path, "mwcch")
    # MSG plus hail probability IR 8.7
    print("MSG plus hail probability IR 8.7")
    mwcch_MSG_087 = "/net/merisi/pbigalke/plots/data_investigation/case_study_20220605/MSG_MWCCH/expats_domain/IR_087"
    mwcch_MSG_imgs_087 = sorted(glob.glob(os.path.join(mwcch_MSG_087, '*.png')))
    print(f"making a gif from {len(mwcch_MSG_imgs_087)} files.")
    gif_maker(mwcch_MSG_imgs_087, f'20220605_mwcch_msg_IR_087', mwcch_gif_path, sec_per_frame=5)

    # # MSG plus hail probability IR 10.8
    # print("MSG plus hail probability IR 10.8")
    # mwcch_MSG_108 = "/net/merisi/pbigalke/plots/data_investigation/case_study_20220605/MSG_MWCCH/expats_domain/IR_108"
    # mwcch_MSG_imgs_108 = sorted(glob.glob(os.path.join(mwcch_MSG_108, '*.png')))
    # print(f"making a gif from {len(mwcch_MSG_imgs_108)} files.")
    # gif_maker(mwcch_MSG_imgs_108, f'20220605_mwcch_msg_IR_108', mwcch_gif_path, sec_per_frame=5)
    
    # # MSG plus hail probability IR 10.8 min 200 max 280
    # print("MSG plus hail probability IR 10.8 min 200 max 280")
    # mwcch_MSG_108_min200_max280 = "/net/merisi/pbigalke/plots/data_investigation/case_study_20220605/MSG_MWCCH/expats_domain/IR_108_min200_max280"
    # mwcch_MSG_imgs_108_min200_max280 = sorted(glob.glob(os.path.join(mwcch_MSG_108_min200_max280, '*.png')))
    # print(f"making a gif from {len(mwcch_MSG_imgs_108_min200_max280)} files.")
    # gif_maker(mwcch_MSG_imgs_108_min200_max280, f'20220605_mwcch_msg_IR_108_min200_max280', mwcch_gif_path, sec_per_frame=5)
    
    # # MSG plus hail probability IR 10.8 - WV 6.2
    # print("MSG plus hail probability IR 10.8 - WV 6.2")
    # mwcch_MSG_062_108 = "/net/merisi/pbigalke/plots/data_investigation/case_study_20220605/MSG_MWCCH/expats_domain/WV_062-IR_108"
    # mwcch_MSG_imgs_062_108 = sorted(glob.glob(os.path.join(mwcch_MSG_062_108, '*.png')))
    # print(f"making a gif from {len(mwcch_MSG_imgs_062_108)} files.")
    # gif_maker(mwcch_MSG_imgs_062_108, f'20220605_mwcch_msg_WV_062-IR_108', mwcch_gif_path, sec_per_frame=5)

    # radar data
    # radar_DWD = "/net/merisi/pbigalke/plots/data_investigation/case_study_20220605/radar_DWD"
    # radar_DWD_imgs = sorted(glob.glob(os.path.join(radar_DWD, '*.png')))
    # print("making a gif from: ")
    # print(radar_DWD)
    # gif_maker(radar_DWD, '20220605_radar_DWD', gif_path, 1)

    # radar and MSG
    # radar_MSG = "/net/merisi/pbigalke/plots/data_investigation/case_study_20220605/radar_and_MSG"
    # radar_MSG_imgs = sorted(glob.glob(os.path.join(radar_MSG, '*.png')))
    # print("making a gif from: ")
    # print(radar_MSG)
    # gif_maker(radar_MSG, '20220605_radar_msg', gif_path, 1)

    # radar and MSG 4-6
    # radar_MSG = "/net/merisi/pbigalke/plots/data_investigation/case_study_20220605/radar_and_MSG_4-6"
    # radar_MSG_imgs = sorted(glob.glob(os.path.join(radar_MSG, '*.png')))
    # print("making a gif from: ", radar_MSG)
    # print("N imgs = ", len(radar_MSG_imgs))
    # gif_maker(radar_MSG_imgs, '20220605_radar_msg_0400-0600', gif_path, sec_per_frame=5)

    # radar and MSG 12-14
    # radar_MSG = "/net/merisi/pbigalke/plots/data_investigation/case_study_20220605/radar_and_MSG_12-14"
    # radar_MSG_imgs = sorted(glob.glob(os.path.join(radar_MSG, '*.png')))
    # print("making a gif from: ", radar_MSG)
    # print("N imgs = ", len(radar_MSG_imgs))
    # gif_maker(radar_MSG_imgs, '20220605_radar_msg_1200-1400', gif_path, sec_per_frame=5)

    # reversed gif 12-14
    # radar_MSG = "/net/merisi/pbigalke/plots/data_investigation/case_study_20220605/radar_and_MSG"
    # times = ["1200", "1220", "1240", "1300", "1320"]
    # #times = ["0500", "0520", "0540"]
    # times_loop = times + list(reversed(times[:-1]))
    # imgs_loop = [f"{radar_MSG}/20220605_{t}_radar_and_msg_IR_108.png" for t in times_loop]
    # for im in imgs_loop:
    #     print(im)
    # print(f"create reverse gif from {int(len(imgs_loop)/2)} images.")
    # gif_maker(imgs_loop, f'20220605_radar_msg_{times[0]}-{times[-1]}_reversed', gif_path, sec_per_frame=5)

    # reversed gif MSG plus hail probability
    # mwcch_MSG = "/net/merisi/pbigalke/plots/data_investigation/case_study_20220605/MSG_MWCCH_rapidscan/german_domain"
    # mwcch_MSG_imgs = sorted(glob.glob(os.path.join(mwcch_MSG, '*.png')))
    # times = ["1200", "1220", "1240", "1300", "1320"]
    # #times = ["0500", "0520", "0540"]
    # times_loop = times + list(reversed(times[:-1]))
    # imgs_loop = [f"{mwcch_MSG}/20220605_{t}_msg_IR_108_poh.png" for t in times_loop]
    # print(f"create reverse gif from {int(len(imgs_loop)/2)} images.")
    # gif_maker(mwcch_MSG_imgs, f'20220605_mwcch_msg', gif_path, sec_per_frame=5)



# %%
if __name__ == '__main__':
    main()

