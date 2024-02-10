import numpy as np
from domain.jump import JUMP_THRESHOLD_MG, Jump
from domain.raw_tile import RawTile
from domain.sync import identifyOffsets
from domain.track import Track
from models.static_registration import StaticRegistration
from models.imu import IMU
from utilities.sig_proc_np import identifyRangesBelowTH, length, lowpass, lowpass
from utilities.quat import eulerToQuat, inverseQuat, quatMult, quatRot, quatToEuler, transformEuler, transformEulerAsXYZ

class Tile:
    def __init__(
            self,
            raw: RawTile,
            prefer_9dof=False,
            print_out=False,
    ):
        self.time = raw.time / 1000
        self.constructProcessedSignals(raw, prefer_9dof, print_out)


    def __printProps__(self, prefix="\t"):
        print(
            prefix,
            "Duration [s]", round(self.time[-1] - self.time[0])
        )


    def constructProcessedSignals(self, raw: RawTile, prefer_9dof: bool, print_out=False):
        """Constructs all the processed signals for the Tile sensor."""
        self.raw_alt = 44307.694 * (1 - (raw.pres / 1013.25)**0.190284)
        self.raw_alt_lpf = lowpass(self.raw_alt, 1/100, 'butter2')
        self.gyro_v = length(raw.gyro)
        self.mG = length(raw.accel)
        self.accel_lpf = lowpass(raw.accel, 3/100, 'butter2')
        self.mG_lpf = length(self.accel_lpf)
        self.imu = IMU(raw.accel, raw.gyro, raw.mag if prefer_9dof else None, print_out=print_out)
        
        # placeholder until the offsets are set from ground truth
        self.alt = self.raw_alt
        self.alt_lpf = self.raw_alt_lpf


    def identifyOffsets(self, 
        truth: list[Track],
        use_lpf=True,
        print_out=False,
    ):
        """Synchronizes the raw tile signals with a ground truth (using a search for best fit),
        correcting altitude & time vectors (x&y) with translational offsets.

        Note: this places the time vector in timestamp format, for comparison to ground truth signals.
        """
        opt_ts, opt_alt = identifyOffsets(
            self.raw_alt_lpf if use_lpf else self.raw_alt,
            use_lpf,
            print_out,
        )
        self.applyOffsets(opt_ts, opt_alt)
        self.applyTimestamp(truth[0].time[0])


    def applyTimestamp(self, ts_global):
        """Applies a static timestamp offset in `s` to the internal time signal.
        
        It's called internally from sync, don't call directly unless you have the timestamp on hand!
        -
        """
        self.time += ts_global - self.time[0]


    def applyOffsets(self, ts_offset, alt_offset):
        """Applies the offsets to the internal time and altitude signal to improve signal accuracy.
        
        It's called internally from sync, don't call directly unless you have the offsets on hand!
        -
        """
        self.time = self.time - (ts_offset / 100)
        self.alt = self.raw_alt - alt_offset
        self.alt_lpf = self.raw_alt_lpf - alt_offset


    def computeJumps(self, print_out=False):
        """Identify all points of low G-force and run the jump id pipeline on each.
        
        Confidence values will be associated with each `Jump` instance.
        """
        lowG_els = identifyRangesBelowTH(self.mG_lpf, JUMP_THRESHOLD_MG)
        self.jumps = [
            Jump(lowG_els[row], self.mG_lpf, self.mG, self.gyro_v, print_out)
            for row in range(lowG_els.shape[0])
        ]


    def computeStaticRegistrations(self, print_out=False):
        """Identifies points for static sensor tile boot registrations.

        Store with an attached timestamp, so that the system computes boot orientations based on new
        registrations (if any pass the tests!)
        """
        self.static_registration = StaticRegistration(self.time, self.alt_lpf, self.mG, self.imu, print_out)


    def computeBootOrientations(self, prototype_sigs=False, print_out=False):
        """Based on the identified static registrations, sensor orientations are transformed into the boot frame.
        
        Since registrations update and contain an associated timestamp, the boot orientations will update whenever
        this happens. Ideally, static registrations would occur at the top of every lift and correct orientations
        on that frequency- otherwise this method will use the most recent registration available for sensor to boot
        orientation transformations.
        """        
        self.boot_quat = np.ones_like(self.imu.quat)
        
        if prototype_sigs:
            q_rot = eulerToQuat(np.array([0, 180, -90]))
            # q_roll90 = np.array([1, 0, 0, 0])
            q_roll90 = np.array([np.sqrt(2) / 2, -np.sqrt(2) / 2, 0, 0])
            self.q_offset_bf = [np.array([1, 0, 0, 0])]
            sensor_euler = np.apply_along_axis(quatToEuler, 1, self.imu.quat)
            self.boot_rotated_euler = np.zeros_like(self.imu.euler)
            self.boot_rotM_euler = np.zeros_like(self.imu.euler)

        for i in range(self.imu.quat.shape[0] - 1):
            q_offset = self.static_registration.getMostRecentRegistrationQuat(self.time[i])
            self.boot_quat[i] = quatRot(self.imu.quat[i], q_offset, inverse=True)
            
            if prototype_sigs:
                # only extracting the horizontal portion of the registrations
                new_euler_offset_bf = quatToEuler(quatRot(q_offset, q_rot, True))
                new_q_offset_bf = inverseQuat(eulerToQuat(np.array([new_euler_offset_bf[0], new_euler_offset_bf[1], 0])))

                if not np.array_equal(new_q_offset_bf, self.q_offset_bf[-1]):
                    self.q_offset_bf.append(new_q_offset_bf)

                self.boot_rotated_euler[i] = quatToEuler(quatMult(quatRot(self.imu.quat[i], q_rot, True), self.q_offset_bf[-1]))
                # self.boot_rotated_euler[i] = quatToEuler(quatRot(self.imu.quat[i], q_rot, True))
                rotM = self.static_registration.getMostRecentRegistrationRotM(self.time[i])
                self.boot_rotM_euler[i] = np.matmul(rotM, sensor_euler[i])

        if print_out:
            print('Transformed sensor orientation into boot frame using the list of static registrations.')


    def computeTurns(self, print_out=False):
        """Identify all turn-based kinematics."""


    @property
    def time(self) -> np.ndarray:
        """Time vector, in `s`. [Nx1]"""
        return self.__time
    
    @time.setter
    def time(self, t):
        self.__time = t


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
    def jumps(self) -> list[Jump]:
        """Jumps identified from kinematic analysis, includes analytics inside the internal `Jump` objects."""
        return self.__jumps
    
    @jumps.setter
    def jumps(self, js):
        self.__jumps = js


    @property
    def imu(self) -> IMU:
        """6/9dof based orientation, default 6dof unless overriden via `init(prefer_9dof)`. Euler: [Nx3], Quat: [Nx4]"""
        return self.__imu
    
    @imu.setter
    def imu(self, i):
        self.__imu = i
        

    @property
    def static_registration(self) -> StaticRegistration:
        """Registration for sensor to boot frame rotations. [1x4]"""
        return self.__static_registration
    
    @static_registration.setter
    def static_registration(self, sr):
        self.__static_registration = sr
        

    @property
    def boot_quat(self) -> np.ndarray:
        """Boot orientation quaternion [Nx4] (rotation) transformed from the sensor orientation and latest 
        available static registration from lift peaks. Using the dof based orientation signals.
        """
        return self.__boot_rot
    
    @boot_quat.setter
    def boot_quat(self, br):
        self.__boot_rot = br
