from track import Track
from tile import Tile
from stitch import stitch

### synchronizes the tile signals with the stitched a50 tracks
### using the altitude as a ground truth
###
### returns tile dataset with global timestamps and corrected altitude
def syncTile(
        tile: Tile,
        truth: [Track],
        printOutput=False,
        printProgress=False,
        use_mae=True,
        time_step_s=0.1,
        max_time_search_s=30,
        alt_step=0.1,
        min_alt_start=0,
        max_alt_search=75):
    tile_alt = tile.raw_alt()
    stitched_a50_time, stitched_a50_alt = stitch(truth)

    # 2. find the optimal time and altitude offsets
    corrected_tile_time = []; corrected_tile_alt = []
    shift_h_tile = []; shift_v_tile = []
    collection = []
    tile_ts_search = 0
    for i in range(max_time_search_s):
        # horizontal shift
        shift_h_tile = tile_alt[tile_ts_search : (tile_ts_search + len(stitched_a50_time) * 100) : 100]

        # reset the elevation starting point
        tile_alt_search = min_alt_start
        for _ in range(int(max_alt_search / alt_step)):
            # vertical shift
            shift_v_tile = [tile - tile_alt_search for tile in shift_h_tile]

            # calculate the mae, sse
            d = [shift_v_tile[k] - stitched_a50_alt[k] for k in range(len(shift_v_tile))]
            abs_d = [abs(_d) for _d in d]
            d2 = [_d**2 for _d in d]
            mae = sum(abs_d) / len(d)
            mse = sum(d2) / len(d)

            # append to lists
            collection.append([tile_ts_search, tile_alt_search, mae, mse])

            # iterate
            tile_alt_search += alt_step

        # iterate (convert since tile time is in ms & publishing at 100Hz)
        tile_ts_search += int(time_step_s * 1000)
        if printProgress:
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
    if printOutput:
        print('Timestamp offset:', opt_ts)
        print('Altitude offset:', opt_alt)
    # converting the timestamps to the global format, which are in seconds
    corrected_tile_time = [((t - tile.time[0]) / 1000) + stitched_a50_time[0] - (opt_ts / 100) for t in tile.time]
    corrected_tile_alt = [a - opt_alt for a in tile_alt]
    return Tile(
        time=corrected_tile_time,
        ax = tile.ax,
        ay = tile.ay,
        az = tile.az,
        gx = tile.gx,
        gy = tile.gy,
        gz = tile.gz,
        mx = tile.mx,
        my = tile.my,
        mz = tile.mz,
        pres = tile.pres,
        temp = tile.temp,
        hum = tile.hum,
        alt=corrected_tile_alt
    )

# Splits the tile data into an array of Tile representing the downhill tracks only.
#
# Optional import of the a50 data to apply the offsets between the 2 ground truths,
# included since the goal is to publish processing signals to f6p, not a50.
def splitTileIntoDownhillTracks(
        tile_sync: Tile,
        f6p: [Track],
        a50: [Track] = [],
        printOutput=False,
        start_offset=True,
        stop_offset=True):
    start_avg = 0
    stop_avg = 0
    if a50:
        ts_splits_f6p = [[track.time[0], track.time[-1]] for track in f6p]
        ts_splits_a50 = [[track.time[0], track.time[-1]] for track in a50]

        for i in range(len(ts_splits_f6p)):
            start_avg += abs(ts_splits_f6p[i][0] - ts_splits_a50[i][0])
            stop_avg += abs(ts_splits_f6p[i][1] - ts_splits_a50[i][1])

        start_avg = round(start_avg / len(ts_splits_f6p))
        stop_avg = round(stop_avg / len(ts_splits_f6p))
        if printOutput:
            print("Avgerage starting and stopping indices:")
            print(start_avg)
            print(stop_avg)

        if not start_offset: start_avg = 0
        if not stop_offset: stop_avg = 0

    # get the start&stop timestamps for every f6p run
    ts_splits = [[track.time[0] - start_avg, track.time[-1] + stop_avg] for track in f6p]

    print(ts_splits)
    # get indices in tile_sync that match these timestamps
    tile_start_idxs = [tile_sync.time.index(split[0]) for split in ts_splits]
    tile_stop_idxs = [tile_sync.time.index(split[1]) for split in ts_splits]

    # split by these timestamps into [Tile]
    tile_runs = []
    for i in range(len(tile_start_idxs)):
        tile_runs.append(
            Tile(
                time=tile_sync.time[tile_start_idxs[i]:tile_stop_idxs[i]],
                ax=tile_sync.ax[tile_start_idxs[i]:tile_stop_idxs[i]],
                ay=tile_sync.ay[tile_start_idxs[i]:tile_stop_idxs[i]],
                az=tile_sync.az[tile_start_idxs[i]:tile_stop_idxs[i]],
                gx=tile_sync.gx[tile_start_idxs[i]:tile_stop_idxs[i]],
                gy=tile_sync.gy[tile_start_idxs[i]:tile_stop_idxs[i]],
                gz=tile_sync.gz[tile_start_idxs[i]:tile_stop_idxs[i]],
                mx=tile_sync.mx[tile_start_idxs[i]:tile_stop_idxs[i]],
                my=tile_sync.my[tile_start_idxs[i]:tile_stop_idxs[i]],
                mz=tile_sync.mz[tile_start_idxs[i]:tile_stop_idxs[i]],
                pres=tile_sync.pres[tile_start_idxs[i]:tile_stop_idxs[i]],
                temp=tile_sync.temp[tile_start_idxs[i]:tile_stop_idxs[i]],
                hum=tile_sync.hum[tile_start_idxs[i]:tile_stop_idxs[i]],
                alt=tile_sync.alt[tile_start_idxs[i]:tile_stop_idxs[i]]
            )
        )
    return tile_runs