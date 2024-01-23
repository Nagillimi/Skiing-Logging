from jump import JUMP_THRESHOLD_MG
from datafile import createJumpDataFile
from tile_track import TileTrack
from decorators import printTracks
from track import Track
from tile import Tile

@printTracks
def splitTileIntoDownhillTileTracks(
        tile_sync: Tile,
        truth: [Track],
        second_truth: [Track] = [],
        print_out=False,
        start_offset=True,
        stop_offset=True,
        header=""):
    """Splits the tile data into an array of Tile representing the downhill tracks only.

    Optional import of the a50 data to apply the offsets between the 2 ground truths,
    included since the goal is to publish processing signals to f6p, not a50.
    """
    start_avg = 0
    stop_avg = 0
    if second_truth:
        ts_splits_truth = [[track.time[0], track.time[-1]] for track in truth]
        ts_splits_truth2 = [[track.time[0], track.time[-1]] for track in second_truth]

        for i in range(len(ts_splits_truth)):
            start_avg += abs(ts_splits_truth[i][0] - ts_splits_truth2[i][0])
            stop_avg += abs(ts_splits_truth[i][1] - ts_splits_truth2[i][1])

        start_avg = round(start_avg / len(ts_splits_truth))
        stop_avg = round(stop_avg / len(ts_splits_truth))
        if print_out:
            print("Avgerage starting and stopping indices:")
            print(start_avg)
            print(stop_avg)

        if not start_offset: start_avg = 0
        if not stop_offset: stop_avg = 0

    # get the start&stop timestamps for every f6p run
    ts_splits = [[track.time[0] - start_avg, track.time[-1] + stop_avg] for track in truth]

    # get indices in tile_sync that match these timestamps
    tile_start_idxs = [tile_sync.time.index(split[0]) for split in ts_splits]
    tile_stop_idxs = [tile_sync.time.index(split[1]) for split in ts_splits]

    file_train = createJumpDataFile(f'logs/tile-{truth[0].date}-jumps-{JUMP_THRESHOLD_MG}mG.csv')

    # split by these timestamps into [Tile]
    tile_runs = [
        TileTrack(
            track_type=truth[i].track_type,
            date=truth[i].date,
            tod=truth[i].tod,
            duration=truth[i].duration,
            length=truth[i].length,
            parent_tile=tile_sync,
            range=[tile_start_idxs[i], tile_stop_idxs[i]],
            file_train=file_train,
            identifyKinematics=True,
        ) for i in range(len(tile_start_idxs))
    ]

    file_train.close()
    return tile_runs
