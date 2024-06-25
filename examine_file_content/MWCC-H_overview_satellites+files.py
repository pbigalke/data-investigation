# %%
import glob
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# %%
path = "/Users/paula/Documents/data/MWCC-H"

years = np.arange(1999, 2024, 1)
months = np.arange(1, 13, 1)

satellites = {# MHS
              'meto01': {'n_files': np.zeros((len(years), len(months))), 'color': 'g', 'instrument': 'MHS'},
              'meto02': {'n_files': np.zeros((len(years), len(months))), 'color': 'g', 'instrument': 'MHS'}, 
              'meto03': {'n_files': np.zeros((len(years), len(months))), 'color': 'g', 'instrument': 'MHS'},
              'noaa15': {'n_files': np.zeros((len(years), len(months))), 'color': 'g', 'instrument': 'MHS'},
              'noaa16': {'n_files': np.zeros((len(years), len(months))), 'color': 'g', 'instrument': 'MHS'},
              'noaa17': {'n_files': np.zeros((len(years), len(months))), 'color': 'g', 'instrument': 'MHS'},
              'noaa18': {'n_files': np.zeros((len(years), len(months))), 'color': 'g', 'instrument': 'MHS'},
              'noaa19': {'n_files': np.zeros((len(years), len(months))), 'color': 'g', 'instrument': 'MHS'}, 
            # ATMS
              'n20': {'n_files': np.zeros((len(years), len(months))), 'color': 'b', 'instrument': 'ATMS'},
              'n21': {'n_files': np.zeros((len(years), len(months))), 'color': 'b', 'instrument': 'ATMS'},
              'npp': {'n_files': np.zeros((len(years), len(months))), 'color': 'b', 'instrument': 'ATMS'},
            # SSMIS
              'f16': {'n_files': np.zeros((len(years), len(months))), 'color': 'r', 'instrument': 'SSMIS'},
              'f17': {'n_files': np.zeros((len(years), len(months))), 'color': 'r', 'instrument': 'SSMIS'},
            # GMI
              'gpm': {'n_files': np.zeros((len(years), len(months))), 'color': 'orange', 'instrument': 'GMI'}}

total_n_files =  np.zeros((len(years), len(months)))

for y, year in enumerate(years):

    for sat in satellites:

        path_instr = f"{path}/{year}/{satellites[sat]['instrument']}"

        files = glob.glob(f"{path_instr}/*.asc.gz")

        if len(files) > 0:
                
            for m, month in enumerate(months):

                date_string = f"{year}{month:02}"

                for f in files:
                    if date_string in f and sat in f.lower():
                        satellites[sat]['n_files'][y, m] += 1
                        total_n_files[y, m] += 1

# %%
# plot overview of used satellites over the years
n_months = len(years)*len(months)
n_sats = len(satellites)

x_month = np.arange(n_months)
y = np.arange(n_sats)

print('plot satellite overview')
"""
sat_overview = f"{path}/sat_overview.png"
f = plt.figure(figsize=(13, 6))
ax = f.add_subplot(111)
ax.yaxis.tick_right()

for s, sat in enumerate(satellites):
    not_None_mask = (satellites[sat]['n_files'].flatten() > 0)
    ax.fill_between(x_month, y[s]-0.25, y[s]+0.25, 
                     where=not_None_mask, 
                     color=satellites[sat]['color'])
ax.set_xticks(x_month[::12], labels=years)
ax.set_yticks(y, labels=[sat for sat in satellites])
ax.set_xlim(0, len(x_month))
ax.grid(axis='x')

# Put a legend below current axis
legend_patches = [mpatches.Patch(color='g', label='MHS'), 
                  mpatches.Patch(color='b', label='ATMS'), 
                  mpatches.Patch(color='r', label='SSMIS'), 
                  mpatches.Patch(color='orange', label='GMI')]
ax.legend(handles=legend_patches, 
          loc='upper center', bbox_to_anchor=(0.5, 1.08),
          fancybox=True, shadow=True, ncol=5)

plt.savefig(sat_overview, bbox_inches='tight')
plt.close()
"""

# %%
##############################################################
print('plot number of files per month')
overpasses_month = f"{path}/overpasses_per_month.png"

x_month = np.arange(n_months)

f = plt.figure(figsize=(20, 6))
ax = f.add_subplot(111)
ax.yaxis.tick_right()
ax.yaxis.set_label_position("right")

bottom = np.zeros(len(x_month))
for s, sat in enumerate(satellites):
    n_files = satellites[sat]['n_files'].flatten()
    p = ax.bar(x_month, n_files, 0.5, color=satellites[sat]['color'], bottom=bottom)
    bottom += n_files

ax.set_xticks(x_month[::12], labels=years)
ax.set_xlim(0, len(x_month))
ax.set_ylabel("number of files")
ax.grid()

# Put a legend below current axis
legend_patches = [mpatches.Patch(color='g', label='MHS'), 
                  mpatches.Patch(color='b', label='ATMS'), 
                  mpatches.Patch(color='r', label='SSMIS'), 
                  mpatches.Patch(color='orange', label='GMI')]
ax.legend(handles=legend_patches, 
          loc='upper center', bbox_to_anchor=(0.5, 1.08),
          fancybox=True, shadow=True, ncol=5)

plt.savefig(overpasses_month, bbox_inches='tight')

# %%
##############################################################
print('plot number of files per year')
overpasses_year = f"{path}/overpasses_per_year.png"

x_year = np.arange(0.5, len(years), 1)

f = plt.figure(figsize=(13, 5))
ax = f.add_subplot(111)
ax.yaxis.tick_right()
ax.yaxis.set_label_position("right")

bottom = np.zeros(len(x_year))
for s, sat in enumerate(satellites):
    n_files_year = np.sum(satellites[sat]['n_files'], axis=1)
    p = ax.bar(x_year, n_files_year, 0.5, color=satellites[sat]['color'], bottom=bottom)
    bottom += n_files_year

ax.set_xticks(x_year, labels=years)
ax.set_xlim(0, len(x_year))
ax.set_ylabel("number of files")
ax.grid()

# Put a legend below current axis
legend_patches = [mpatches.Patch(color='g', label='MHS'), 
                  mpatches.Patch(color='b', label='ATMS'), 
                  mpatches.Patch(color='r', label='SSMIS'), 
                  mpatches.Patch(color='orange', label='GMI')]
ax.legend(handles=legend_patches, 
          loc='upper center', bbox_to_anchor=(0.5, 1.08),
          fancybox=True, shadow=True, ncol=5)

plt.savefig(overpasses_year, bbox_inches='tight')

print("DONE")

