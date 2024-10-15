# %%
import numpy as np
import sys
sys.path.append("..")
import readers.read_processed_MWCC_H as mwcch_read
import matching_data.collect_matching_files as match

# %%
def create_file_list_per_area_thresholds(years, months, area_thresholds=[10, 20, 30, 40, 50, 60]):
    """collect all files with overpass area larger than area_threshold and save to txt files

    Parameters
    ----------
    area_threshold : list of int, optional
        _description_, by default 30
    """
    mwcch_path = mwcch_read.MWCCH_MSGGRID_PATH

    year_range = f"{years[0]}-{years[-1]}"
    month_range = f"{months[0]}-{months[-1]}"
    output_file_name = f"{mwcch_path}/file_lists_studies/files_{year_range}_{month_range}"

    # create txt file for each threshold
    for t in area_thresholds:
        with open(f"{output_file_name}_areathresh{t}.txt", "w") as f:
            # add header to file
            f.write(f"Files with area larger than {t}%\n")

    count = 0
    # loop over subfolders
    for year in years:
        for month in months:
            # collect all mwcc-h files in this month
            mwcch_files = match.get_files_in_study_period(mwcch_path, year, months=month)

            # loop over files
            for file in mwcch_files:
                # read in dataset
                mwcch_data = mwcch_read.read(file, variables=["hail_class"]).hail_class.values

                # get covered area percentage
                area_perc = mwcch_read.get_area_percentage_covered_by_overpass(mwcch_data)

                # check if area is larger than threshold
                for t in area_thresholds:
                    if area_perc >= t:
                        # write to respective file
                        with open(f"{output_file_name}_areathresh{t}.txt", "a") as f:
                            f.write(f"{file}\n")

                if count % 1000 == 0:
                    print(f"{count}", flush=True)
                count += 1

def read_txt_file_into_list(file_path):
    """Read a text file into a list, skipping the first row.

    Parameters
    ----------
    file_path : str
        Path to the text file.

    Returns
    -------
    list
        List of lines from the file, excluding the first row.
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()[1:]  # Read all lines and skip the first one
    return [line.strip() for line in lines]  # Strip newline characters

# %%
if __name__ == "__main__":
    years = np.arange(2006, 2024, 1)
    months = np.arange(4, 10, 1)
    create_file_list_per_area_thresholds(years, months)
# %%
