import numpy as np
from domain.devices.track import Track

def stitch(trackList: list[Track]):
    return np.array([track.time for track in trackList]),\
        np.array([track.alt for track in trackList])