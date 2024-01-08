import pandas as pd
from tile import Tile
from track import Track
from datetime import datetime

def decode_A50(file, printProps=False):
    csv = pd.read_csv(file)
    l = csv.loc[csv['SkiApp PRO 2.3.10 - Available in Google PlayStore'].isnull()].isnull().index.to_list()
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
        time = [int(t) + _datetime.timestamp() for t in vectors.iloc[:, 0].tolist()]
        dist = [float(d) for d in vectors.iloc[:, 1].tolist()]
        vel = [float(v) / 3.6 for v in vectors.iloc[:, 2].tolist()] # originally in kmh
        course = [int(c) for c in vectors.iloc[:, 3].tolist()]
        alt = [float(a) for a in vectors.iloc[:, 4].tolist()]
        lat = [float(l) for l in vectors.iloc[:, 5].tolist()]
        long = [float(l) for l in vectors.iloc[:, 6].tolist()]
        acc = [int(a) for a in vectors.iloc[:, 7].tolist()]

        trackObj = Track(
            type=type,
            date=date,
            tod=tod,
            duration=duration,
            length=length,
            time=time,
            dist=dist,
            vel=vel,
            course=course,
            alt=alt,
            lat=lat,
            long=long,
            acc=acc
        )
        if printProps: trackObj.__printProps__()
        tracks.append(trackObj)
    return tracks

def decode_A50_downhill(file, printProps=False):
    tracks = decode_A50(file, printProps)
    return [track for track in tracks if track.type == "Downhill"]

def decode_F6P(file, printProps=False):
    ts_offset = 631065600 # Special Garmin constant... https://stackoverflow.com/a/57836047
    csv = pd.read_csv(file, low_memory=False) # no low memory due to columns having data with nonintersecting types
    lap_rows = csv.loc[csv['Message'] == 'lap'].loc[csv['Type'] == 'Data']
    lap_indices = [0] + lap_rows.index.tolist()
    tracks = []
    total_dist = 0

    for n in range(len(lap_indices) - 1):
        track = csv.iloc[lap_indices[n]:lap_indices[n + 1]].loc[csv['Message'] == 'record'].loc[csv['Type'] == 'Data']
        start_ts = int(lap_rows.iloc[n, 7])
        _datetime = datetime.fromtimestamp(start_ts + ts_offset)
        date = _datetime.date()
        tod = _datetime.time()
        duration = int(lap_rows.iloc[n, 25])
        length = float(lap_rows.iloc[n, 28])

        time = [int(t) - 1 + ts_offset for t in track.iloc[:, 4].tolist()]
        dist = [float(d) - total_dist for d in track.iloc[:, 13].tolist()] # since this is accumulating distance
        vel = [float(v) for v in track.iloc[:, 16].tolist()]
        course = []
        alt = [float(a) for a in track.iloc[:, 19].tolist()]
        lat = [float(l) * 180 / (2**31) for l in track.iloc[:, 7].tolist()] # convert from sc to deg
        long = [float(l) * 180 / (2**31) for l in track.iloc[:, 10].tolist()] # convert from sc to deg
        acc = []

        trackObj = Track(
            type="Downhill",
            date=date,
            tod=tod,
            duration=duration,
            length=length,
            time=time,
            dist=dist,
            vel=vel,
            course=course,
            alt=alt,
            lat=lat,
            long=long,
            acc=acc
        )
        if printProps: trackObj.__printProps__()
        tracks.append(trackObj)

        total_dist += length
    return tracks

def decode_tile(file):
    csv = pd.read_csv(file)
    return Tile(
        time=[int(t) for t in csv.iloc[:, 0].tolist()],
        ax=[int(a) for a in csv.iloc[:, 1].tolist()],
        ay=[int(a) for a in csv.iloc[:, 2].tolist()],
        az=[int(a) for a in csv.iloc[:, 3].tolist()],
        gx=[int(g) for g in csv.iloc[:, 4].tolist()],
        gy=[int(g) for g in csv.iloc[:, 5].tolist()],
        gz=[int(g) for g in csv.iloc[:, 6].tolist()],
        mx=[int(m) for m in csv.iloc[:, 7].tolist()],
        my=[int(m) for m in csv.iloc[:, 8].tolist()],
        mz=[int(m) for m in csv.iloc[:, 9].tolist()],
        pres=[float(p) for p in csv.iloc[:, 10].tolist()],
        temp=[float(t) for t in csv.iloc[:, 11].tolist()],
        hum=[float(h) for h in csv.iloc[:, 12].tolist()])