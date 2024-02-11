import datetime as dt

class Track:
    def __init__(
            self,
            track_type: str,
            date: dt.date,
            tod: dt.time,
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


    @property
    def track_type(self) -> str:
        """Track type string, either `Downhill`, `Walk`, `Hold`, or `Lift`."""
        return self.__track_type
    
    @track_type.setter
    def track_type(self, tt):
        self.__track_type = tt


    @property
    def date(self) -> dt.date:
        """Recording date of session track. `datetime.date`"""
        return self.__date
    
    @date.setter
    def date(self, d):
        self.__date = d


    @property
    def tod(self) -> dt.time:
        """Recording time of day of session track. `datetime.time`"""
        return self.__tod
    
    @tod.setter
    def tod(self, tod):
        self.__tod = tod


    @property
    def duration(self) -> int:
        """Duration (static) of session track, in `s`."""
        return self.__duration
    
    @duration.setter
    def duration(self, d):
        self.__duration = d


    @property
    def length(self) -> int:
        """Length/3D distance of session track, in `m`."""
        return self.__length
    
    @length.setter
    def length(self, l):
        self.__length = l


    @property
    def time(self) -> list[int]:
        """Time vector, in `s`."""
        return self.__time
    
    @time.setter
    def time(self, t):
        self.__time = t


    @property
    def dist(self) -> list[float]:
        """3D distance vector, in `m`."""
        return self.__dist
    
    @dist.setter
    def dist(self, d):
        self.__dist = d


    @property
    def vel(self) -> list[float]:
        """Velocity vector, in `m/s`."""
        return self.__vel
    
    @vel.setter
    def vel(self, v):
        self.__vel = v


    @property
    def alt(self) -> list[float]:
        """Altitude vector in `m` above sea level. Depends on the device on whether it was
        derived from barometric or mapped GPS data.
        """
        return self.__alt
    
    @alt.setter
    def alt(self, a):
        self.__alt = a


    @property
    def lat(self) -> list[float]:
        """Lattitude vector, in `°`."""
        return self.__lat
    
    @lat.setter
    def lat(self, l):
        self.__lat = l


    @property
    def long(self) -> list[float]:
        """Longitude vector, in `°`."""
        return self.__long
    
    @long.setter
    def long(self, l):
        self.__long = l


    @property
    def var(self) -> list[int]:
        """Variance of GPS/Accuracy vector, in `m`."""
        return self.__var
    
    @var.setter
    def var(self, v):
        self.__var = v


    @property
    def course(self) -> list[float]:
        """Course vector/heading of GPS position based on causal velocity, in `°`."""
        return self.__course
    
    @course.setter
    def course(self, c):
        self.__course = c
