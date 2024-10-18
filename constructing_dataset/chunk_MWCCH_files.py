# %%
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
sys.path.append('..')
import MWCCH_file_lists_for_studies as mwcch_list
import readers.read_processed_MWCC_H as mwcch_read
import matching_data.collect_matching_files as match


# %%
def chunk_files_by_timerange(files, n_frames, msg_res, gap=15, start_match="following", chunk_match="previous", cropsize=128):

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
    plotpath = "/net/merisi/pbigalke/plots/data_investigation/constructing_dataset/chunking_MWCCH_files"
    if not os.path.exists(plotpath):
        os.makedirs(plotpath)

    # study period settings
    years = [2022]
    months = [6]

    # time series settings
    msg_res = 15
    n_frames = 4
    cropsize = 128

    area_thresholds = np.arange(0, 70, 10)
    # t = 0
    gaps = np.arange(15, 70, 15)
    # g=15
    
    start_match=["following", "closest"]
    chunk_match=["previous", "following", "closest"]


    ###### plot chunking of MWCCH files per gap for different area thresholds #######
    fig, axes = plt.subplots(2, 4, figsize=(15, 10))
    plot_colors = ['r', 'g', 'b', 'c', 'm', 'y']
    n_max_files = 0
    
    for t, thresh in enumerate(area_thresholds):
        ax = axes[t//4, t%4]

        count_line = 0
        for start in start_match:
            for chunk in chunk_match:
                # print("start match:", start, "chunk match:", chunk)
                # for t in area_thresholds:
                n_files = []
                n_chunks = []
                for g in gaps:
                    mwcch_files = mwcch_list.read_mwcch_files_for_study_settings(mwcch_path, years, months, thresh)
                    chunks = chunk_files_by_timerange(mwcch_files, n_frames, msg_res, start_match=start, chunk_match=chunk, gap=g)
                    # print("area threshold:", t, "# files:", len(mwcch_files), "# chunks:", len(chunks))
                    # print("gap:", g, "# files:", len(mwcch_files), "# chunks:", len(chunks))
                    n_files.append(len(mwcch_files))
                    n_chunks.append(len(chunks))
                    if t == 0:
                        n_max_files = len(mwcch_files)
                
                if count_line == 0:
                    ax.set_title(f"area thresh = {thresh}%")
                    
                ax.plot(gaps, n_chunks, label=f"({start}/{chunk})", color=plot_colors[count_line])
                count_line += 1
        # draw x label if in last row
        if t//4 == 1:
            ax.set_xlabel("Gap between time series [min]")
        # draw y label if in first column
        if t%4 == 0:
            ax.set_ylabel("# chunks")
        ax.set_ylim(95, 350)
        ax.grid()

        # draw legend only for the last subplot and move it outside the plot to the right
        if t == len(area_thresholds)-1:
            ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    # turn off last subplot
    ax = axes[-1, -1]
    ax.axis('off')

    fig.suptitle(f"Chunking {n_max_files} MWCCH files")
    plt.savefig(f"{plotpath}/chunking_mwcch_files_per_gap_for_diff_thresh.png")
    plt.show()
    plt.close()

    # ####### plot chunking of MWCCH files per area thresh for different gaps #######
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    plot_colors = ['r', 'g', 'b', 'c', 'm', 'y']
    n_max_files = 0
    for g, gap in enumerate(gaps):
        ax = axes[g//2, g%2]

        count_line = 0
        for start in start_match:
            for chunk in chunk_match:
                # print("start match:", start, "chunk match:", chunk)
                # for t in area_thresholds:
                n_files = []
                n_chunks = []
                for t, thresh in enumerate(area_thresholds):
                    mwcch_files = mwcch_list.read_mwcch_files_for_study_settings(mwcch_path, years, months, thresh)
                    chunks = chunk_files_by_timerange(mwcch_files, n_frames, msg_res, start_match=start, chunk_match=chunk, gap=gap)
                    # print("area threshold:", t, "# files:", len(mwcch_files), "# chunks:", len(chunks))
                    # print("gap:", g, "# files:", len(mwcch_files), "# chunks:", len(chunks))
                    n_files.append(len(mwcch_files))
                    n_chunks.append(len(chunks))
                    if t == 0:
                        n_max_files = len(mwcch_files)
                
                if count_line == 0:
                    ax.set_title(f"gap = {gap}min")
                
                ax.plot(area_thresholds, n_chunks, label=f"({start}/{chunk})", color=plot_colors[count_line])
                count_line += 1
        # draw x label if in last row
        if g//2 == 1:
            ax.set_xlabel("Area threshold [%]")
        # draw y label if in first column
        if g%2 == 0:
            ax.set_ylabel("# chunks")
        # ax.set_ylim(95, 350)
        ax.grid()
        ax.set_ylim(90, 500)

        # draw legend only for the last subplot and move it outside the plot to the right
        if g == len(gaps)-1:
            ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
            
            # plot total number of files in upper right subplot
            # get axes for lower right plot
            ax = axes[0, 2]
            ax.plot(area_thresholds, n_files, label="total", color='k')
            ax.set_title("total amount of files")
            ax.set_ylabel("# files")
            ax.grid()

    # turn off last subplot
    ax = axes[-1, -1]
    ax.axis('off')

    fig.suptitle(f"Chunking {len(n_max_files)} MWCCH files")
    plt.savefig(f"{plotpath}/chunking_mwcch_files_per_areathresh_for_diff_gaps.png")
    plt.show()
    plt.close()





# %%
