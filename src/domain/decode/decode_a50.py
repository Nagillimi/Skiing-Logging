import datetime as dt
import pandas as pd
from domain.devices.track import Track
from domain.session_logger import SessionLogger as logger
from utilities.decorators.print_tracks import printTracks


@printTracks
def decodeA50(file):
    csv = pd.read_csv(file)
    logger.info(f'Imported A50 data from csv, rows: {csv.size}')

    l = csv.loc[csv.iloc[:, 0].isnull()].index.to_list()
    nan_indices = [0] + l + [csv.shape[0]]
    tracks = []

    for n in range(len(nan_indices) - 1):
        track = csv.iloc[nan_indices[n]:nan_indices[n+1]].dropna(how="all")
        properties = track.iloc[0, 0]
        type = properties.split("\"")[1]
        fulltime = properties.split("@ ")[1].split(', Duration=')[0].replace('p.', 'P').replace('m.', 'M').replace('a.', 'A')
        durlength = properties.split("@ ")[1].split(', Duration=')[1]
        # https://docs.python.org/2/library/datetime.html#strftime-and-strptime-behavior
        _datetime = dt.datetime.strptime(fulltime, '%b. %d, %Y, %I:%M:%S %p')
        date = _datetime.date()
        tod = _datetime.time()
        duration = int(durlength.split("'")[0]) * 60 + int(durlength.split("'")[1])
        length = int(durlength.split("Length=")[1].replace('m', ''))

        vectors = track.iloc[2:, :]
        time = [int(float(t)) + int(_datetime.timestamp()) for t in vectors.iloc[:, 0].tolist()]
        dist = [float(d) for d in vectors.iloc[:, 1].tolist()]
        vel = [float(v) / 3.6 for v in vectors.iloc[:, 2].tolist()] # originally in kmh
        course = [int(c) for c in vectors.iloc[:, 3].tolist()]
        alt = [float(a) for a in vectors.iloc[:, 4].tolist()]
        lat = [float(l) for l in vectors.iloc[:, 5].tolist()]
        long = [float(l) for l in vectors.iloc[:, 6].tolist()]
        var = [int(a) for a in vectors.iloc[:, 7].tolist()]

        trackObj = Track(
            track_type=type,
            date=date,
            tod=tod,
            duration=duration,
            length=length,
            time=time,
            dist=dist,
            vel=vel,
            alt=alt,
            lat=lat,
            long=long,
            var=var,
            course=course
        )
        tracks.append(trackObj)

    
    logger.info(f'Decoded A50 data into {len(tracks)} tracks.')
    return tracks


@printTracks
def decodeA50Downhill(file):
    tracks = decodeA50(file)
    return [track for track in tracks if track.track_type == "Downhill"]
