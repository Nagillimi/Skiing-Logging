import numpy as np
from stitch import stitch
from track import Track


def identifyOffsets(
    tile_alt: np.ndarray, 
    truth: [Track],
    print_out=False,
    print_progress=False,
    use_mae=True,
    time_step_s=0.1,
    max_time_search_s=30,
    alt_step=0.1,
    min_alt_start=0,
    max_alt_search=75,
):
    """Synchronizes the raw tile signals with a ground truth (using a search for best fit),
    correcting altitude & time vectors (x&y) with translational offsets.

    Note: this places the time vector in timestamp format, for comparison to ground truth signals.
    """
    stitched_a50_time, stitched_a50_alt = stitch(truth)

    # 2. find the optimal time and altitude offsets
    shift_h_tile = []; shift_v_tile = []
    collection = []
    tile_ts_search = 0
    for i in range(max_time_search_s):
        # horizontal shift & downsample to 1Hz (for truth comparison)
        shift_h_tile = tile_alt[tile_ts_search : (tile_ts_search + len(stitched_a50_time) * 100) : 100]

        # reset the elevation starting point
        tile_alt_search = min_alt_start
        for _ in range(round(max_alt_search / alt_step)):
            # vertical shift
            shift_v_tile = shift_h_tile - tile_alt_search

            # calculate the mae, sse
            d = shift_v_tile - stitched_a50_alt
            abs_d = np.abs(d)
            d2 = d**2
            mae = np.mean(abs_d)
            mse = np.mean(d2)

            # append to lists
            collection.append([tile_ts_search, tile_alt_search, mae, mse])

            # iterate
            tile_alt_search += alt_step

        # iterate (in seconds)
        tile_ts_search += int(time_step_s * 1000)
        if print_progress:
            progress = round(100 * (i + 1) / (max_time_search_s + 1))
            print(progress, '%', sep="")
    
    ts_all = [m[0] for m in collection]
    alt_all = [m[1] for m in collection]
    mae_all = [m[2] for m in collection]
    mse_all = [m[3] for m in collection]
    min_ts_idx = 0
    if use_mae: min_ts_idx = mae_all.index(min(mae_all))
    else: min_ts_idx = mse_all.index(min(mse_all))

    # 3. Align the timestamp with the start of the a50 dataset, incorporating the offset
    opt_ts = ts_all[min_ts_idx] 
    opt_alt = alt_all[min_ts_idx]
    if print_out:
        print('Synchronized Tile Parameters')
        print('\tTimestamp offset (ms):', opt_ts)
        print('\tAltitude offset (m):', opt_alt)

    return opt_ts, opt_alt