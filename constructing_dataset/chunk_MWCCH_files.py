# %%
import numpy as np
import os
import sys
sys.path.append('..')
import MWCCH_file_lists_for_studies as mwcch_list
import readers.read_processed_MWCC_H as mwcch_read
import matching_data.collect_matching_files as match


# %%
def chunk_files_by_timerange(files, n_frames, msg_res, gap=15, start_match="following", chunk_match="previous"):

    # Parse timestamps of scanning end time
    files_with_timestamps = [(file, mwcch_read.get_scan_datetime_from_mwcch_filepath(file, which="end")) for file in files]

    # sort files by timestamp in descending order
    files_with_timestamps.sort(key=lambda x: x[1], reverse=True)

    # Chunk files based on the specified time range
    chunks = []
    current_chunk = []
    current_start_time = None
    current_end_time = None
    timeseries_length = np.timedelta64((n_frames-1)*msg_res, 'm')
    gap_length = np.timedelta64(gap, 'm')

    # loop over all files
    for file, timestamp in files_with_timestamps:

        # get corresponding MSG timestamps if this would be timeseries start
        msg_last_frame = match.get_closest_MSG_timestamps(timestamp, which=start_match, msg_res=msg_res)
        
        # get corresponding MSG timestamps to check if this file is within the time range
        msg_chunk_match = match.get_closest_MSG_timestamps(timestamp, which=chunk_match, msg_res=msg_res)


        # check if this is the first file
        if current_start_time is None:
            # set current start time to corresponding MSG timestamp of the first file
            current_start_time = msg_last_frame
            # set respective end time
            current_end_time = current_start_time - timeseries_length

            # add file to current chunk
            current_chunk.append(file)

        #check if file is within range of current chunk
        elif (current_start_time - msg_chunk_match) <= timeseries_length:
            # add file to current chunk
            current_chunk.append(file)

        else:
            # file is out of bound for previous chunk

            # if current chunk is not empty, add it to final list
            if current_chunk:
                chunks.append(current_chunk)

            # check if gap of current file to previous timeseries is large enough to start new chunk
            if (current_end_time - msg_last_frame) >= gap_length:
                current_chunk = [file]
                # set new start time to corresponding MSG timestamp of the current file
                current_start_time = msg_last_frame
                # set respective end time
                current_end_time = current_start_time - timeseries_length
            else:
                # do not start new chunk
                current_chunk = []

    if current_chunk:
        chunks.append(current_chunk)

    return chunks

# %%
if __name__ == "__main__":

    mwcch_path = mwcch_read.MWCCH_MSGGRID_PATH

    # study period settings
    years = [2022]
    months = [6]

    # time series settings
    msg_res = 15
    n_frames = 4
    cropsize = 128

    area_thresholds = np.arange(0, 70, 10)
    
    start_match=["following", "closest"]
    chunk_match=["previous", "following", "closest"]

    for start in start_match:
        for chunk in chunk_match:
            print("start match:", start, "chunk match:", chunk)
            for t in area_thresholds:
                mwcch_files = mwcch_list.read_mwcch_files_for_study_settings(mwcch_path, years, months, t)
                chunks = chunk_files_by_timerange(mwcch_files, n_frames, msg_res, start_match=start, chunk_match=chunk)
                print("area threshold:", t, "# files:", len(mwcch_files), "# chunks:", len(chunks))


# %%
