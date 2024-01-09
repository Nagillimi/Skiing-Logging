from datetime import date, time

class Track:
    def __init__(
            self,
            type: str,
            date: date,
            tod: time,
            duration: int,
            length: int,
            time: list[int],
            dist: list[float],
            vel: list[float],
            course: list[float],
            alt: list[float],
            lat: list[float],
            long: list[float],
            acc: list[int]
    ):
        # props
        self.type = type
        self.date = date
        self.tod = tod
        self.duration = duration
        self.length = length

        # vectors
        self.time = time
        self.dist = dist
        self.vel = vel
        self.course = course
        self.alt = alt
        self.lat = lat
        self.long = long
        self.acc = acc

    def __printProps__(self):
        print(
            "Track type", self.type, "|",
            "Date", self.date, "|",
            "Time", self.tod, "|",
            "Duration [s]", self.duration, "|",
            "Length [m]", self.length
        )