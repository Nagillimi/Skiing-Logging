import pandas as pd
from domain.devices.raw_tile import RawTile
from domain.session_logger import SessionLogger as logger
from utilities.decorators.print_tracks import printTracks


@printTracks
def decodeTile(file, header=''):
    csv = pd.read_csv(file)
    logger.info(f'Imported Tile data from csv, dimensions: {csv.size}')

    return RawTile(
        time=csv.iloc[:, 0].to_numpy(),
        accel=csv.iloc[:, 1:4].to_numpy(),
        gyro=csv.iloc[:, 4:7].to_numpy(),
        mag=csv.iloc[:, 7:10].to_numpy(),
        pres=csv.iloc[:, 10].to_numpy(),
        temp=csv.iloc[:, 11].to_numpy(),
        hum=csv.iloc[:, 12].to_numpy(),
    )

