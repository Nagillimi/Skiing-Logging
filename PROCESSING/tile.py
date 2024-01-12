class Tile:
    def __init__(
            self,
            time: list[float],
            ax: list[int], ay: list[int], az: list[int],
            gx: list[int], gy: list[int], gz: list[int],
            mx: list[int], my: list[int], mz: list[int],
            pres: list[float],
            temp: list[float],
            hum: list[float],
            alt: list[float],
    ):
        self.time = time
        self.ax = ax
        self.ay = ay
        self.az = az
        self.gx = gx
        self.gy = gy
        self.gz = gz
        self.mx = mx
        self.my = my
        self.mz = mz
        self.pres = pres
        self.temp = temp
        self.hum = hum
        self.alt = alt

    # converts the pressure data in mB to altitude in m, using:
    # https://www.weather.gov/media/epz/wxcalc/pressureAltitude.pdf
    # will still need to account for (relatively constant) weather offsets!
    def raw_alt(self):
        return [44307.694 * (1 - (p / 1013.25)**0.190284) for p in self.pres]
    
    def imu6dof(self):
        pass

    def imu9dof(self):
        pass