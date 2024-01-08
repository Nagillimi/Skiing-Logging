class Track:
    def __init__(
            self,
            type,
            date,
            tod,
            duration,
            length,
            time,
            dist,
            vel,
            course,
            alt,
            lat,
            long,
            acc):
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