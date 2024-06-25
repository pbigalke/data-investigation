# %%
import imageio
import glob

def create_gif(filenames, gif_path):
    images = []
    for filename in filenames:
        images.append(imageio.imread(filename))
    imageio.mimsave(gif_path, images, format='GIF', fps=2)

path = "/net/merisi/pbigalke/plots/data_investigation/case_study_20220605/MSG_MWCCH/german_domain/*"
filenames = sorted(glob.glob(path))
print(filenames)
gif_path = "output/20220605_germandomain.gif"
create_gif(filenames, gif_path)


# %%
