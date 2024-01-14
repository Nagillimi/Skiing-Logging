def stitch(trackList):
    t = []; a = []
    for track in trackList: t += track.time; a += track.alt
    return t, a