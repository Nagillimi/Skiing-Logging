from domain.session_logger import SessionLogger as logger


def printTracks(func):
    """Prints the track details for the decoded file."""
    def wrapper(*args, **kwargs):
        logger.debug(kwargs.get("header", "Unknown device"))

        tracks = func(*args, **kwargs)

        if isinstance(tracks, list):
            [track.__printProps__() for track in tracks]
        else:
            tracks.__printProps__()

        return tracks
    return wrapper