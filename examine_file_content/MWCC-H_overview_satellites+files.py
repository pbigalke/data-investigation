# %%
import glob
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
import os

def main():
  datapath = "/net/merisi/pbigalke/data/MWCC-H/MWCC-H"
  plotpath = "/net/merisi/pbigalke/plots/data_investigation/MWCC-H"
  if not os.path.exists(plotpath):
     os.makedirs(plotpath)
  years = np.arange(1999, 2024, 1)
  months = np.arange(4, 10, 1)

  # count number of files per year, month and satellite
  satellites, total_n_files = count_occurences(datapath, years, months)

  # plot satellite deployment overview
  sat_overview = f"{plotpath}/sat_overview_apr-sep.png"
  plot_satellite_deployment_overview(years, months, satellites, sat_overview, figsize=(20, 6))

  # plot occurence per month and satellite
  overpasses_month = f"{plotpath}/overpasses_per_month_apr-sep.png"
  plot_occurences_per_month(years, months, satellites, overpasses_month, figsize=(25, 6))

  # plot occurence per year and satellite
  overpasses_year = f"{plotpath}/overpasses_per_year_apr-sep.png"
  plot_occurences_per_year(years, satellites, overpasses_year, figsize=(13, 6))

def count_occurences(path, years, months):

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

  return satellites, total_n_files

def plot_satellite_deployment_overview(years, months, satellites, output_name, figsize=(13, 6)):
  # plot overview of used satellites over the years
  n_months = len(months)
  n_years = len(years)
  n_sats = len(satellites)

  x_month = np.arange(n_months*n_years)
  y = np.arange(n_sats)

  f = plt.figure(figsize=figsize)
  ax = f.add_subplot(111)
  ax.yaxis.tick_right()

  for s, sat in enumerate(satellites):
      not_None_mask = (satellites[sat]['n_files'].flatten() > 0)
      ax.fill_between(x_month, y[s]-0.25, y[s]+0.25, 
                      where=not_None_mask, 
                      color=satellites[sat]['color'])
  # set major ticks
  ax.xaxis.set_major_locator(MultipleLocator(n_months))
  ax.set_xticklabels(years)

  # set minor ticks
  ax.xaxis.set_minor_locator(MultipleLocator(1))
  ax.xaxis.set_tick_params(which='minor', grid_linestyle='--')

  # set y ticks
  ax.set_yticks(y, labels=[sat for sat in satellites])

  # set limits and grid
  ax.set_xlim(0, len(x_month))
  ax.grid(axis='x', which="both")

  # Put a legend below current axis
  legend_patches = [mpatches.Patch(color='g', label='MHS'), 
                    mpatches.Patch(color='b', label='ATMS'), 
                    mpatches.Patch(color='r', label='SSMIS'), 
                    mpatches.Patch(color='orange', label='GMI')]
  ax.legend(handles=legend_patches, 
            loc='upper center', bbox_to_anchor=(0.5, 1.08),
            fancybox=True, shadow=True, ncol=5)

  plt.savefig(output_name, bbox_inches='tight')
  plt.close()

def plot_occurences_per_month(years, months, satellites, output_name, figsize=(20, 6)):
  n_months = len(months)
  n_years = len(years)
  x_month = np.arange(n_months*n_years)

  f = plt.figure(figsize=figsize)
  ax = f.add_subplot(111)
  ax.yaxis.tick_right()
  ax.yaxis.set_label_position("right")

  bottom = np.zeros(len(x_month))
  for sat in satellites:
      n_files = satellites[sat]['n_files'].flatten()
      p = ax.bar(x_month, n_files, 0.8, color=satellites[sat]['color'], bottom=bottom, align="edge")
      bottom += n_files

  # set major ticks
  ax.xaxis.set_major_locator(MultipleLocator(n_months))
  ax.set_xticklabels(years)

  # set minor ticks
  ax.xaxis.set_minor_locator(MultipleLocator(1))
  ax.xaxis.set_tick_params(which='minor', grid_linestyle='--')

  # Turn off y-axis minor ticks
  ax.yaxis.set_tick_params(which='minor', right=False)
  ax.set_ylabel("number of files")

  # set limits and grid
  ax.set_xlim(0, len(x_month))
  ax.grid(axis='x', which="both")

  # Put a legend below current axis
  legend_patches = [mpatches.Patch(color='g', label='MHS'), 
                    mpatches.Patch(color='b', label='ATMS'), 
                    mpatches.Patch(color='r', label='SSMIS'), 
                    mpatches.Patch(color='orange', label='GMI')]
  ax.legend(handles=legend_patches, 
            loc='upper center', bbox_to_anchor=(0.5, 1.08),
            fancybox=True, shadow=True, ncol=5)

  plt.savefig(output_name, bbox_inches='tight')
  plt.close()


def plot_occurences_per_month_and_satellite(years, months, satellites, output_name, figsize=(20, 10)):
  n_months = len(months)
  n_years = len(years)
  n_sats = len(satellites)
  x_month = np.arange(n_months*n_years)

  f, axes = plt.subplots(n_sats)
  f.set_figheight(figsize[1])
  f.set_figwidth(figsize[0])

  for s, sat in enumerate(satellites):
      ax = axes[s]
      n_files = satellites[sat]['n_files'].flatten()
      p = ax.bar(x_month, n_files, 0.8, color=satellites[sat]['color'], bottom=bottom, align="edge")
      bottom += n_files
  ax.yaxis.tick_right()
  ax.yaxis.set_label_position("right")


  # set major ticks
  ax.xaxis.set_major_locator(MultipleLocator(n_months))
  ax.set_xticklabels(years)

  # set minor ticks
  ax.xaxis.set_minor_locator(MultipleLocator(1))
  ax.xaxis.set_tick_params(which='minor', grid_linestyle='--')

  # Turn off y-axis minor ticks
  ax.yaxis.set_tick_params(which='minor', right=False)
  ax.set_ylabel("number of files")

  # set limits and grid
  ax.set_xlim(0, len(x_month))
  ax.grid(axis='x', which="both")

  # Put a legend below current axis
  legend_patches = [mpatches.Patch(color='g', label='MHS'), 
                    mpatches.Patch(color='b', label='ATMS'), 
                    mpatches.Patch(color='r', label='SSMIS'), 
                    mpatches.Patch(color='orange', label='GMI')]
  ax.legend(handles=legend_patches, 
            loc='upper center', bbox_to_anchor=(0.5, 1.08),
            fancybox=True, shadow=True, ncol=5)

  plt.savefig(output_name, bbox_inches='tight')
  plt.close()

def plot_occurences_per_year(years, satellites, output_name, figsize=(13, 6)):
  
  x_year = np.arange(0.5, len(years), 1)

  f = plt.figure(figsize=figsize)
  ax = f.add_subplot(111)
  ax.yaxis.tick_right()
  ax.yaxis.set_label_position("right")

  bottom = np.zeros(len(x_year))
  for sat in satellites:
      n_files_year = np.sum(satellites[sat]['n_files'], axis=1)
      p = ax.bar(x_year, n_files_year, 0.8, color=satellites[sat]['color'], bottom=bottom, align="edge")
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

  plt.savefig(output_name, bbox_inches='tight')
  plt.close()


# %%
if __name__ == "__main__":
   main()
# %%
