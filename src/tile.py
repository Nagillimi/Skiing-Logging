from jump import JUMP_THRESHOLD_MG, Jump
from raw_tile import RawTile
from registration import Registration
from sync import timeAndAltOffsets
from imu import IMU
from signal_processing import identifyRangesBelowTH, length, lowpass, lowpass3
import numpy as np

from track import Track

class Tile:
    def __init__(
            self,
            raw: RawTile,
    ):
        self.time = raw.time
        """Time vector, in `s`. [Nx1]"""

        self.constructProcessedSignals(raw)


    def __printProps__(self, prefix="\t"):
        in_s = self.time[1] - self.time[0] <= 0.01
        print(
            prefix,
            "Duration [s]", round((self.time[-1] - self.time[0]) / (1 if in_s else 1000))
        )


    @property
    def raw_alt(self) -> np.ndarray:
        """Converts the pressure data in mB to altitude in m, using:
        https://www.weather.gov/media/epz/wxcalc/pressureAltitude.pdf.

        Will still need to account for (relatively constant) weather offsets!
        [Nx1]
        """
        return self.__raw_alt
    
    @raw_alt.setter
    def raw_alt(self, ra):
        self.__raw_alt = ra


    @property
    def raw_alt_lpf(self) -> np.ndarray:
        """Filtered raw (no offset) altitude signal with a 2nd order 1/100 LP butterworth filter. [Nx1]"""
        return self.__raw_alt_lpf

    @raw_alt_lpf.setter
    def raw_alt_lpf(self, ral):
        self.__raw_alt_lpf = ral


    @property
    def alt(self) -> np.ndarray:
        """Offset altitude signal based on ground truth and is set inside `sync()`. [Nx1]"""
        return self.__alt
    
    @alt.setter
    def alt(self, ra):
        self.__alt = ra


    @property
    def alt_lpf(self) -> np.ndarray:
        """Filtered offset altitude signal with a 2nd order 1/100 LP butterworth filter. [Nx1]"""
        return self.__alt_lpf

    @alt_lpf.setter
    def alt_lpf(self, ral):
        self.__alt_lpf = ral


    @property
    def gyro_v(self) -> np.ndarray:
        """Unfiltered 3D gyroscopic vector magnitude.  [Nx1]"""
        return self.__gyro_v
    
    @gyro_v.setter
    def gyro_v(self, g):
        self.__gyro_v = g


    @property
    def mG(self) -> np.ndarray:
        """Unfiltered mG-forces (3D accelerometer vector magnitude). [Nx1]"""
        return self.__mG

    @mG.setter
    def mG(self, mg):
        self.__mG = mg


    @property
    def accel_lpf(self) -> np.ndarray:
        """Filtered accelerometer signals. [Nx1]"""
        return self.__accel_lpf
    
    @accel_lpf.setter
    def accel_lpf(self, al):
        self.__accel_lpf = al


    @property
    def mG_lpf(self) -> np.ndarray:
        """Filtered mG-forces. [Nx1]"""
        return self.__mG_lpf
    
    @mG_lpf.setter
    def mG_lpf(self, mgl):
        self.__mG_lpf = mgl
    

    @property
    def imu6(self) -> IMU:
        """6dof based orientation. Euler: [Nx3], Quat: [Nx4]"""
        return self.__imu6
    
    @imu6.setter
    def imu6(self, i6):
        self.__imu6 = i6
        
    
    @property
    def imu9(self) -> IMU:
        """9dof based orientation. Euler: [Nx3], Quat: [Nx4]"""
        return self.__imu9
    
    @imu9.setter
    def imu9(self, i9):
        self.__imu9 = i9


    @property
    def qSB_6(self) -> [Registration]:
        """Registration for sensor to boot frame rotations, based on 6dof. [1x4]"""
        return self.__qSB_6
    
    @qSB_6.setter
    def qSB_6(self, qsb6):
        self.__qSB_6 = qsb6
        
    
    @property
    def qSB_9(self) -> [Registration]:
        """Registration for sensor to boot frame rotations, based on 9dof. [1x4]"""
        return self.__qSB_9
    
    @qSB_9.setter
    def qSB_9(self, qsb9):
        self.__qSB_9 = qsb9
    

    @property
    def jumps(self) -> [Jump]:
        """Jumps identified from kinematic analysis, includes analytics inside the internal `Jump` objects."""
        return self.__jumps
    
    @jumps.setter
    def jumps(self, qsb9):
        self.__jumps = qsb9


    def constructProcessedSignals(self, raw: RawTile):
        """Constructs all the processed signals for the Tile sensor."""

        self.raw_alt = 44307.694 * (1 - (raw.pres / 1013.25)**0.190284)
        self.raw_alt_lpf = lowpass(self.raw_alt, 1/100, 'butter2')
        self.gyro_v = length(raw.gyro)
        self.mG = length(raw.accel)

        self.accel_lpf = lowpass3(raw.accel, 3/100, 'butter2')
        self.mG_lpf = length(self.accel_lpf)

        self.imu6 = IMU(raw.accel, raw.gyro)
        self.imu9 = IMU(raw.accel, raw.gyro, raw.mag)


    def identifyOffsets(self, 
        truth: [Track],
        use_lpf=True,
        print_out=False,
        print_progress=False,
        use_mae=True,
        time_step_s=0.1,
        max_time_search_s=30,
        alt_step=0.1,
        min_alt_start=0,
        max_alt_search=75,
    ):
        """Synchronizes the raw tile signals with a ground truth (using a search for best fit),
        correcting altitude & time vectors (x&y) with translational offsets.

        Note: this places the time vector in timestamp format, for comparison to ground truth signals.
        """
        self.applyOffsets(
            timeAndAltOffsets(
                self,
                truth,
                use_lpf,
                print_out,
                print_progress,
                use_mae,
                time_step_s,
                max_time_search_s,
                alt_step,
                min_alt_start,
                max_alt_search
            )
        )
        self.applyTimestamp(truth[0].time[0])


    def applyTimestamp(self, ts_global):
        """Applies a static timestamp offset in `s` to the internal time signal.
        
        It's called internally from sync, don't call directly unless you have the timestamp on hand!
        -
        """
        self.time += ts_global - (self.time[0] / 1000)


    def applyOffsets(self, ts_offset, alt_offset):
        """Applies the offsets to the internal time and altitude signal to improve signal accuracy.
        
        It's called internally from sync, don't call directly unless you have the offsets on hand!
        -
        """
        self.time = (self.time / 1000) - (ts_offset / 100)
        self.alt = self.raw_alt - alt_offset
        self.alt_lpf = self.raw_alt_lpf - alt_offset


    def computeJumps(self, override_th=None):
        """Identify all points of low G-force and run the jump id pipeline on each.
        
        Confidence values will be associated with each `Jump` instance.
        """
        lowG_els = identifyRangesBelowTH(
            self.mG_lpf(),
            JUMP_THRESHOLD_MG if override_th is None else override_th
        )
        self.jumps = [Jump(el, self.mG_lpf(), self.mG, self.gyro) for el in lowG_els]
        self.logJumpData(override_th)


    def computeStaticRegistrations(self):
        """Identifies points for static sensor tile boot registrations.

        Store with an attached timestamp, so that the system computes boot orientations based on new
        registrations (if any pass the tests!)
        """
        self.qSB6 = [Registration]
        self.qSB9 = [Registration]


    def computeTurns(self):
        """Identify all turn-based kinematics."""
