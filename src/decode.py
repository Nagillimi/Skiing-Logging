import pandas as pd
from decorators import printTracks
from raw_tile import RawTile
from track import Track
from datetime import datetime


@printTracks
def decodeA50(file, print_out, header):
    csv = pd.read_csv(file)
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
        _datetime = datetime.strptime(fulltime, '%b. %d, %Y, %I:%M:%S %p')
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
    return tracks


@printTracks
def decodeA50Downhill(file, print_out, header):
    tracks = decodeA50(file, print_out=False, header="")
    return [track for track in tracks if track.track_type == "Downhill"]


@printTracks
def decodeF6P(file, print_out, header):
    ts_msb = 631065600 # Add MSB since this is the LSB of the ts https://stackoverflow.com/a/57836047
    csv = pd.read_csv(file, low_memory=False) # no low memory due to columns having data with nonintersecting types
    lap_rows = csv.loc[csv['Message'] == 'lap'].loc[csv['Type'] == 'Data']
    lap_indices = [0] + lap_rows.index.tolist()
    tracks = []
    total_dist = 0

    for n in range(len(lap_indices) - 1):
        track = csv.iloc[lap_indices[n]:lap_indices[n + 1]].loc[csv['Message'] == 'record'].loc[csv['Type'] == 'Data']
        start_ts = int(lap_rows.iloc[n, 7])
        _datetime = datetime.fromtimestamp(start_ts + ts_msb)
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
    return tracks


@printTracks
def decodeTile(file, print_out, header):
    csv = pd.read_csv(file)

    return RawTile(
        time=csv.iloc[:, 0].to_numpy(),
        accel=csv.iloc[:, 1:4].to_numpy(),
        gyro=csv.iloc[:, 4:7].to_numpy(),
        mag=csv.iloc[:, 7:10].to_numpy(),
        pres=csv.iloc[:, 10].to_numpy(),
        temp=csv.iloc[:, 11].to_numpy(),
        hum=csv.iloc[:, 12].to_numpy(),
    )