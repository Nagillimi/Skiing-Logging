from track import Track
from tile import Tile
import math

### synchronizes the tile signals with the stitched a50 tracks
### using the altitude as a ground truth
###
### returns tile dataset with global timestamps and corrected altitude
def syncTile(
        tile: Tile,
        a50: [Track],
        print_progress=True,
        use_mae=True,
        time_step_s=0.1,
        max_time_search_s=30,
        alt_step=0.1,
        min_alt_start=0,
        max_alt_search=75):
    tile_alt = tile.raw_alt()
    
    # 1. stich the a50 tracks
    stitched_a50_time = []
    stitched_a50_alt = []
    for track in a50:
        stitched_a50_time += track.time
        stitched_a50_alt += track.alt

    # 2. find the optimal time and altitude offsets
    corrected_tile_time = []
    corrected_tile_alt = []
    shift_h_tile = []
    shift_v_tile = []
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
            mae = math.fsum(abs_d) / len(d)
            mse = math.fsum(d2) / len(d)

            # append to lists
            collection.append([tile_ts_search, tile_alt_search, mae, mse])

            # iterate
            tile_alt_search += alt_step

        # iterate (convert since tile time is in ms & publishing at 100Hz)
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