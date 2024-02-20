import datetime as dt
import pandas as pd
from domain.devices.track import Track
from domain.session_logger import SessionLogger as logger
from utilities.decorators.print_tracks import printTracks


@printTracks
def decodeF6P(file):
    ts_msb = 631065600 # Add MSB since this is the LSB of the ts https://stackoverflow.com/a/57836047
    csv = pd.read_csv(file, low_memory=False) # no low memory due to columns having data with nonintersecting types
    logger.info(f'Imported F6P data from csv, rows: {csv.size}')

    lap_rows = csv.loc[csv['Message'] == 'lap'].loc[csv['Type'] == 'Data']
    lap_indices = [0] + lap_rows.index.tolist()
    tracks = []
    total_dist = 0

    for n in range(len(lap_indices) - 1):
        track = csv.iloc[lap_indices[n]:lap_indices[n + 1]].loc[csv['Message'] == 'record'].loc[csv['Type'] == 'Data']
        start_ts = int(lap_rows.iloc[n, 7])
        _datetime = dt.datetime.fromtimestamp(start_ts + ts_msb)
        date = _datetime.date()
        tod = _datetime.time()
        duration = int(lap_rows.iloc[n, 25])
        length = float(lap_rows.iloc[n, 28])

        time = [int(t) + ts_msb for t in track.iloc[:, 4].tolist()]
        dist = [float(d) - total_dist for d in track.iloc[:, 13].tolist()] # since this is accumulating distance
        vel = [float(v) for v in track.iloc[:, 16].tolist()]
        alt = [float(a) for a in track.iloc[:, 19].tolist()]
        lat = [float(l) * 180 / (2**31) for l in track.iloc[:, 7].tolist()] # convert from sc to deg
        long = [float(l) * 180 / (2**31) for l in track.iloc[:, 10].tolist()] # convert from sc to deg

        trackObj = Track(
            track_type="Downhill",
            date=date,
            tod=tod,
            duration=duration,
            length=length,
            time=time,
            dist=dist,
            vel=vel,
            alt=alt,
            lat=lat,
            long=long
        )
        tracks.append(trackObj)

        total_dist += length
        
    logger.info(f'Decoded F6P data into {len(tracks)} tracks.')
    return tracks
