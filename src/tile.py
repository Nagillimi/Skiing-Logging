from tile_track import TileTrack
from quat import avgQuat
from imu import IMU
from signal_processing import length, lowpass
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
            imu6=None,
            imu9=None,
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
        """Corrected/offset alt set from sync, using the ground truth to account constant offsets"""

        self.imu6 = IMU([ax, ay, az], [gx, gy, gz]) if imu6 is None else imu6
        """6dof based orientation"""

        self.imu9 = IMU([ax, ay, az], [gx, gy, gz], [mx, my, mz]) if imu9 is None else imu9
        """9dof based orientation"""

        self.qSB6 = np.array([1., 0., 0., 0.])
        """6dof sensor frame to boot frame rotation, [w, x, y, z]."""

        self.qSB9 = np.array([1., 0., 0., 0.])
        """9dof sensor frame to boot frame rotation, [w, x, y, z]."""


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


    @property
    def tracks(self):
        return self.__tracks


    @property
    def file_train(self):
        return self.__file_train


    @file_train.setter
    def file_train(self, f):
        self.__file_train = f


    def assignTracks(self, ranges):
        self.__tracks = [
            TileTrack(
                track_type='Downhill',
                parent_tile=self,
                range=r,
                file_train=self.file_train,
                identifyKinematics=True,
            ) for r in ranges
        ]


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
    

    def getTrack(self, idx: int):
        """Instantiates TileTrack for the downhill track based on the downhill track index."""
        return self.tracks[idx]


    def setQsbFromRange(self, r):
        """Set the rotation quaternion to rotate the sensor frame into the boot frame."""
        self.qSB6 = avgQuat(self.imu6.quat[r[0]:r[1]])
        self.qSB9 = avgQuat(self.imu9.quat[r[0]:r[1]])
        print('setQsbFromRange() qSB6 set to:', self.qSB6)
        print('setQsbFromRange() qSB9 set to:', self.qSB9)

