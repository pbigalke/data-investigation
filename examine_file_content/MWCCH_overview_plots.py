# %%
import glob
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import MultipleLocator, AutoMinorLocator
import os

def satellite_counter(years, months, extra_dim=1):
  satellites = {# MHS
                'meto01': {'count': np.zeros((len(years), len(months), extra_dim)), 'color': 'g', 'instrument': 'MHS'},
                'meto02': {'count': np.zeros((len(years), len(months), extra_dim)), 'color': 'g', 'instrument': 'MHS'}, 
                'meto03': {'count': np.zeros((len(years), len(months), extra_dim)), 'color': 'g', 'instrument': 'MHS'},
                'noaa15': {'count': np.zeros((len(years), len(months), extra_dim)), 'color': 'g', 'instrument': 'MHS'},
                'noaa16': {'count': np.zeros((len(years), len(months), extra_dim)), 'color': 'g', 'instrument': 'MHS'},
                'noaa17': {'count': np.zeros((len(years), len(months), extra_dim)), 'color': 'g', 'instrument': 'MHS'},
                'noaa18': {'count': np.zeros((len(years), len(months), extra_dim)), 'color': 'g', 'instrument': 'MHS'},
                'noaa19': {'count': np.zeros((len(years), len(months), extra_dim)), 'color': 'g', 'instrument': 'MHS'}, 
              # ATMS
                'n20': {'count': np.zeros((len(years), len(months), extra_dim)), 'color': 'b', 'instrument': 'ATMS'},
                'n21': {'count': np.zeros((len(years), len(months), extra_dim)), 'color': 'b', 'instrument': 'ATMS'},
                'npp': {'count': np.zeros((len(years), len(months), extra_dim)), 'color': 'b', 'instrument': 'ATMS'},
              # SSMIS
                'f16': {'count': np.zeros((len(years), len(months), extra_dim)), 'color': 'r', 'instrument': 'SSMIS'},
                'f17': {'count': np.zeros((len(years), len(months), extra_dim)), 'color': 'r', 'instrument': 'SSMIS'},
              # GMI
                'gpm': {'count': np.zeros((len(years), len(months), extra_dim)), 'color': 'orange', 'instrument': 'GMI'}}
  return satellites

def plot_satellite_deployment_overview(years, months, satellite_counter, output_name, figsize=(13, 6)):
  # plot overview of used satellites over the years
  n_months = len(months)
  n_years = len(years)
  n_sats = len(satellite_counter)

  x_month = np.arange(n_months*n_years)
  y = np.arange(n_sats)

  f = plt.figure(figsize=figsize)
  ax = f.add_subplot(111)
  ax.yaxis.tick_right()

  for s, sat in enumerate(satellite_counter):
      not_None_mask = (satellite_counter[sat]['count'].flatten() > 0)
      ax.fill_between(x_month, y[s]-0.25, y[s]+0.25, 
                      where=not_None_mask, 
                      color=satellite_counter[sat]['color'])
  # set major ticks
  ax.xaxis.set_major_locator(MultipleLocator(n_months))
  ax.set_xticklabels(np.append("", years))  # locators start at -n_months so we need to add an aditional label

  # set minor ticks
  ax.xaxis.set_minor_locator(MultipleLocator(1))
  ax.xaxis.set_tick_params(which='minor', grid_linestyle='--')

  # set y ticks
  ax.set_yticks(y, labels=[sat for sat in satellite_counter])

  # set limits and grid
  ax.set_xlim(0, len(x_month))
  ax.grid(axis='x', which="both")

  # Put a legend below current axis
  legend_patches = [mpatches.Patch(color='g', label='MHS'), 
                    mpatches.Patch(color='b', label='ATMS'), 
                    mpatches.Patch(color='r', label='SSMIS'), 
                    mpatches.Patch(color='orange', label='GMI')]
  ax.legend(handles=legend_patches, 
            loc='upper left', bbox_to_anchor=(0.05, 1.08),
            fancybox=True, shadow=True, ncol=5)

  plt.savefig(output_name, bbox_inches='tight')
  plt.close()

def plot_occurrences_per_month(years, months, satellite_counter, output_name, figsize=(20, 6)):
  n_months = len(months)
  n_years = len(years)
  x_month = np.arange(n_months*n_years)

  f = plt.figure(figsize=figsize)
  ax = f.add_subplot(111)
  ax.yaxis.tick_right()
  ax.yaxis.set_label_position("right")

  bottom = np.zeros(len(x_month))
  for sat in satellite_counter:
      n_files = satellite_counter[sat]['count'].flatten()
      p = ax.bar(x_month, n_files, 0.8, color=satellite_counter[sat]['color'], bottom=bottom, align="edge")
      bottom += n_files

  # set major ticks
  ax.xaxis.set_major_locator(MultipleLocator(n_months))
  ax.set_xticklabels(np.append("", years))  # locators start at -n_months so we need to add an aditional label

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
            loc='upper left', bbox_to_anchor=(0.05, 1.08),
            fancybox=True, shadow=True, ncol=5)

  plt.savefig(output_name, bbox_inches='tight')
  plt.close()

def plot_occurrences_per_month_and_satellite(years, months, satellite_counter, output_name, figsize=(20, 10)):
  n_months = len(months)
  n_years = len(years)
  n_sats = len(satellite_counter)
  x_month = np.arange(n_months*n_years)

  f, axes = plt.subplots(n_sats)
  f.set_figheight(figsize[1])
  f.set_figwidth(figsize[0])

  for s, sat in enumerate(satellite_counter):
    ax = axes[-(s+1)]
    n_files = satellite_counter[sat]['count'].flatten()
    p = ax.bar(x_month, n_files, 0.8, color=satellite_counter[sat]['color'], align="edge")

    # write satellite in top left corner
    ax.text(.01, .9, sat, ha='left', va='top', transform=ax.transAxes)

    ax.yaxis.tick_right()
    ax.yaxis.set_label_position("right")

    # set major ticks
    ax.xaxis.set_major_locator(MultipleLocator(n_months))
    if s == 0:
      # somehow the locations of the ticks start at -6, 
      # so the first year is not written within plotting range starting from 0
      # this is why we add another label at the beginning
      ax.set_xticklabels(np.append("", years))
    else:
      ax.set_xticklabels("")

    # set minor ticks
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.xaxis.set_tick_params(which='minor', grid_linestyle='--')

    # Turn off y-axis minor ticks
    ax.yaxis.set_tick_params(which='minor', right=False)
    if s == len(axes)/2:
       ax.set_ylabel("number of files")

    # set limits and grid
    ax.set_xlim(0, len(x_month))
    ax.set_ylim(0, 200)
    ax.grid(which="both")

  # Put a legend below current axis
  legend_patches = [mpatches.Patch(color='g', label='MHS'), 
                    mpatches.Patch(color='b', label='ATMS'), 
                    mpatches.Patch(color='r', label='SSMIS'), 
                    mpatches.Patch(color='orange', label='GMI')]
  ax.legend(handles=legend_patches, 
            loc='upper left', bbox_to_anchor=(0.05, 1.08),
            fancybox=True, shadow=True, ncol=5)

  plt.savefig(output_name, bbox_inches='tight')
  plt.close()

def plot_occurrences_per_year(years, satellites, output_name, figsize=(13, 6)):
  
  x_year = np.arange(0.5, len(years), 1)

  f = plt.figure(figsize=figsize)
  ax = f.add_subplot(111)
  ax.yaxis.tick_right()
  ax.yaxis.set_label_position("right")

  bottom = np.zeros(len(x_year))
  for sat in satellites:
      n_files_year = np.sum(satellites[sat]['count'], axis=(1, -1))
      p = ax.bar(x_year - 0.4, n_files_year, 0.8, color=satellites[sat]['color'], bottom=bottom, align="edge")
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
            loc='upper left', bbox_to_anchor=(0.05, 1.08),
            fancybox=True, shadow=True, ncol=5)

  plt.savefig(output_name, bbox_inches='tight')
  plt.close()



# %%
