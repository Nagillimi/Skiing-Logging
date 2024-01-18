from jump import Jump
from signal_processing import identifyRangesBelowTH, length, lowpass
import imufusion
import numpy as np

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
    def gyro(self):
        """Unfiltered Gyroscope (3D gyroscopic vector magnitude)"""
        return length(self.gx, self.gy, self.gz)      


    @property
    def mG(self):
        """Unfiltered mG-forces (3D accelerometer vector magnitude)"""
        return length(self.ax, self.ay, self.az)


    def ax_lpf(self, Wn=5/100, ftype='iir1'):
        """5/100 Lowpass filtered accelerometer data for x"""
        return lowpass(self.ax, Wn, ftype=ftype)


    def ay_lpf(self, Wn=5/100, ftype='iir1'):
        """5/100 Lowpass filtered accelerometer data for y"""
        return lowpass(self.ay, Wn, ftype=ftype)


    def az_lpf(self, Wn=5/100, ftype='iir1'):
        """5/100 Lowpass filtered accelerometer data for z"""
        return lowpass(self.az, Wn, ftype=ftype)      


    def mG_lpf(self, Wn=3/100, ftype='iir1'):
        """mG-forces based on 3/100 lowpass filtered accelerometer values"""
        return length(
            self.ax_lpf(ftype=ftype, Wn=Wn), 
            self.ay_lpf(ftype=ftype, Wn=Wn), 
            self.az_lpf(ftype=ftype, Wn=Wn)
        )


    def identifyJumps(self):
        """Identify all points of low G-force and run the jump id pipeline on each.
        
        Confidence values will be associated with each `Jump` instance.
        """
        lowG_els = identifyRangesBelowTH(self.mG_lpf(), Jump.mGThreshold())
        self.jumps = [Jump(el, self.mG_lpf(), self.mG, self.gyro) for el in lowG_els]

    
    def identifyTurns(self): pass


    def imu9dof(self):
        offset = imufusion.Offset(100)
        ahrs = imufusion.Ahrs()
        ahrs.settings = imufusion.Settings(imufusion.CONVENTION_NWU,  # convention
                                   0.5,  # gain
                                   2000,  # gyroscope range
                                   10,  # acceleration rejection
                                   10,  # magnetic rejection
                                   5 * 100)  # recovery trigger period = 5 seconds

        euler_9dof = np.empty((len(self.time), 3))
        for i in range(len(self.time)):
            gyro = np.array([self.gx[i], self.gy[i], self.gz[i]])
            offset_gyro = offset.update(gyro)
            accel = np.array([self.ax_lpf()[i], self.ay_lpf()[i], self.az_lpf()[i]])
            mag = np.array([self.mx[i], self.my[i], self.mz[i]])

            ahrs.update(offset_gyro, accel, mag, 0.01)
            euler_9dof[i] = ahrs.quaternion.to_euler()
        return euler_9dof
