from jump import Jump
from signal_processing import identifyRangesBelowTH, length, lowpass

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
            corrected_alt: list[float],
            identifyKinematics=True
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
        self.corrected_alt = corrected_alt
        if not identifyKinematics:
            return
        self.identifyJumps()
        self.identifyTurns()


    @property
    def raw_alt(self):
        """Converts the pressure data in mB to altitude in m, using:
        https://www.weather.gov/media/epz/wxcalc/pressureAltitude.pdf.

        Will still need to account for (relatively constant) weather offsets!
        """
        return [44307.694 * (1 - (p / 1013.25)**0.190284) for p in self.pres]


    @property
    def ax_lpf(self):
        """5/100 Lowpass filtered accelerometer data for x"""
        return lowpass(self.ax, fc=5, fs=100)


    @property
    def ay_lpf(self):
        """5/100 Lowpass filtered accelerometer data for y"""
        return lowpass(self.ay, fc=5, fs=100)


    @property
    def az_lpf(self):
        """5/100 Lowpass filtered accelerometer data for z"""
        return lowpass(self.az, fc=5, fs=100)      


    @property
    def gyro(self):
        """Unfiltered Gyroscope (3D gyroscopic vector magnitude)"""
        return length(self.gx, self.gy, self.gz)      


    @property
    def mG(self):
        """Unfiltered mG-forces (3D accelerometer vector magnitude)"""
        return length(self.ax, self.ay, self.az)      


    @property
    def mG_lpf(self):
        """15/100 Lowpass filtered mG-forces"""
        return lowpass(length(self.ax_lpf, self.ay_lpf, self.az_lpf), fc=15, fs=100)      


    def identifyJumps(self):
        """Identify all points of low G-force and run the jump id pipeline on each.
        
        Confidence values will be associated with each `Jump` instance.
        """
        lowG_els = identifyRangesBelowTH(self.mG_lpf, Jump.mGThreshold())
        self.jumps = [Jump(el, self.mG_lpf, self.mG, self.gyro) for el in lowG_els]

    
    def identifyTurns(self): pass


    def imu6dof(self): pass
        

    def imu9dof(self): pass

