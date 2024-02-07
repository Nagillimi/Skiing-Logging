from datetime import date, time

class Track:
    def __init__(
            self,
            track_type: str,
            date: date,
            tod: time,
            duration: int,
            length: int,
            time: list[int],
            dist: list[float],
            vel: list[float],
            alt: list[float],
            lat: list[float],
            long: list[float],
            var: list[int] = [],
            course: list[float] = []
    ):
        # props
        self.track_type = track_type
        self.date = date
        self.tod = tod
        self.duration = duration
        self.length = length

        # vectors
        self.time = time
        self.dist = dist
        self.vel = vel
        self.alt = alt
        self.lat = lat
        self.long = long
        self.var = var
        self.course = course

    def __printProps__(self, prefix="\t"):
        print(
            prefix,
            "Track type", self.track_type, "|",
            "Date", self.date, "|",
            "Time", self.tod, "|",
            "Duration [s]", self.duration, "|",
            "Length [m]", self.length
        )