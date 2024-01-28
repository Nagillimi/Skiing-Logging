from track import Track
import numpy as np

def stitch(trackList: [Track]):
    return np.array([track.time for track in trackList]),\
        np.array([track.alt for track in trackList])