import pandas as pd
from utilities.decorators import printTracks
from domain.raw_tile import RawTile


@printTracks
def decodeTile(file, print_out, header=''):
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