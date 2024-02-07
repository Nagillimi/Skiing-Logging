

def printTestResults(func):
    """Prints the test header & results to console in a readable format."""
    def wrapper(*args, **kwargs):
        if kwargs.get("print_out"):
            print(kwargs.get("header"))
        result = func(*args, **kwargs)
        if kwargs.get("print_out"):
            print('\t', result, sep='')
        return result
    return wrapper


def printTracks(func):
    """Prints the track details for the decoded file."""
    def wrapper(*args, **kwargs):
        if kwargs.get("print_out") is True:
            print(kwargs.get("header", "Unknown device"))

        tracks = func(*args, **kwargs)

        if kwargs.get("print_out") is True:        
            if isinstance(tracks, list):
                [track.__printProps__() for track in tracks]
            else:
                tracks.__printProps__()
        return tracks
    return wrapper
