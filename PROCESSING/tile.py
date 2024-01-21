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
            corrected_alt: list[float]
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
        # set from the sync, using the ground truth to account constant offsets
        self.corrected_alt = corrected_alt
        self.euler6 = self.computeEuler6()
        self.euler9 = self.computeEuler9()


    def __printProps__(self, prefix="\t"):
        in_s = self.time[1] - self.time[0] <= 0.01
        print(
            prefix,
            "Duration [s]", round((self.time[-1] - self.time[0]) / (1 if in_s else 1000))
        )


    @property
    def raw_alt(self):
        """Converts the pressure data in mB to altitude in m, using:
        https://www.weather.gov/media/epz/wxcalc/pressureAltitude.pdf.

        Will still need to account for (relatively constant) weather offsets!
        """
        return [44307.694 * (1 - (p / 1013.25)**0.190284) for p in self.pres]


    @property
    def raw_alt_lpf(self):
        """Converts the pressure data in mB to altitude in m, using:
        https://www.weather.gov/media/epz/wxcalc/pressureAltitude.pdf.

        Will still need to account for (relatively constant) weather offsets (that's the "raw" part)!

        Filtered with a 2nd order 1/100 LP butterworth filter
        """
        return lowpass(self.raw_alt, 1/100, 'butter2')


    @property
    def gyro(self):
        """Unfiltered Gyroscope (3D gyroscopic vector magnitude)"""
        return length(self.gx, self.gy, self.gz)      


    @property
    def mG(self):
        """Unfiltered mG-forces (3D accelerometer vector magnitude)"""
        return length(self.ax, self.ay, self.az)


    def computeEuler9(self):
        """IMU Sensor Fusion data based on 9dof sensors, (accel, gyro, mag).
        
        Gyro angles corrected with gravity vector from the accelerometer frame & 
        heading signals from the magnetometer frame.
        """
        offset = imufusion.Offset(100)
        ahrs = imufusion.Ahrs()
        ahrs.settings = imufusion.Settings(imufusion.CONVENTION_NWU,  # convention
                                   0.5,  # gain
                                   2000,  # gyroscope range
                                   10,  # acceleration rejection
                                   10,  # magnetic rejection
                                   5 * 100)  # recovery trigger period = 5 seconds

        euler = np.empty((len(self.time), 3))
        for i in range(len(self.time)):
            gyro = np.divide([self.gx[i], self.gy[i], self.gz[i]], 1000) #mdps -> dps
            offset_gyro = offset.update(gyro)
            accel = np.divide([self.ax[i], self.ay[i], self.az[i]], 1000) #mG -> G
            mag = np.divide([self.mx[i], self.my[i], self.mz[i]], 10) # mgauss -> uT

            ahrs.update(offset_gyro, accel, mag, 1 / 100)
            euler[i] = ahrs.quaternion.to_euler()
        return euler


    def computeEuler6(self):
        """IMU Sensor Fusion data based on 6dof sensors, (accel, gyro).
        
        Gyro angles corrected with gravity vector from the accelerometer frame.
        """
        ahrs = imufusion.Ahrs()

        euler = np.empty((len(self.time), 3))
        for i in range(len(self.time)):
            gyro = np.divide([self.gx[i], self.gy[i], self.gz[i]], 1000) #mdps -> dps
            accel = np.divide([self.ax[i], self.ay[i], self.az[i]], 1000) #mG -> G
            ahrs.update_no_magnetometer(gyro, accel, 1 / 100)  # 100 Hz sample rate
            euler[i] = ahrs.quaternion.to_euler()
        return euler


    def ax_lpf(self, Wn, ftype):
        """Lowpass filtered accelerometer data for x"""
        return lowpass(self.ax, Wn, ftype=ftype)


    def ay_lpf(self, Wn, ftype):
        """Lowpass filtered accelerometer data for y"""
        return lowpass(self.ay, Wn, ftype=ftype)


    def az_lpf(self, Wn, ftype):
        """Lowpass filtered accelerometer data for z"""
        return lowpass(self.az, Wn, ftype=ftype)      


    def mG_lpf(self, Wn=3/100, ftype='butter2'):
        """mG-forces based on 3/100 lowpass filtered accelerometer values"""
        return length(
            self.ax_lpf(Wn=Wn, ftype=ftype), 
            self.ay_lpf(Wn=Wn, ftype=ftype), 
            self.az_lpf(Wn=Wn, ftype=ftype)
        )
