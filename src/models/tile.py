import numpy as np
from constants.jump_th import JUMP_THRESHOLD_MG
from constants.turn_th import D_MG_LPF_DT_TH
from domain.devices.raw_tile import RawTile
from domain.devices.track import Track
from domain.g_force import GForce
from domain.session_logger import SessionLogger as logger
from models.geography import Geography
from models.jump import Jump
from models.static_registration import StaticRegistration
from models.imu import IMU
from models.turn import Turn
from utilities.frames import convertToBootFrame
from utilities.sig_proc_np import identifyLTThInsideRanges, length, lowpass, lowpass, zeroCrossingIdxsGTThInsideRanges
from utilities.sync import identifyOffsets
from utilities.quat import quatMult, quatToEuler

class Tile:
    def __init__(
            self,
            raw: RawTile,
            prefer_9dof=False,
            compute_kinematics=True,
    ):
        self.time = raw.time / 1000
        self.constructProcessedSignals(raw, prefer_9dof)

        if not compute_kinematics:
            return
        
        self.identifyGeographicalPoints()
        self.identifyJumps()
        self.identifyStaticRegistrations()
        self.computeBootOrientations()
        self.identifyTurns()


    def __printProps__(self=None, prefix="\t"):
        logger.debug(f'{prefix}Duration [s]", {round(self.time[-1] - self.time[0])}')


    def constructProcessedSignals(self, raw: RawTile, prefer_9dof: bool=None):
        """Constructs all the processed signals for the Tile sensor."""
        logger.info(f'Constructing all processed signals.')

        self.raw_alt = 44307.694 * (1 - (raw.pres / 1013.25)**0.190284)
        self.raw_alt_lpf = lowpass(self.raw_alt, 1/100, 'butter2')
        self.gyro_v = length(raw.gyro)
        self.imu = IMU(raw.accel, raw.gyro, raw.mag if prefer_9dof else None)
        self.g_force = GForce(raw.accel)

        # placeholder until the offsets are set from ground truth
        self.alt = self.raw_alt
        self.alt_lpf = self.raw_alt_lpf


    def identifyOffsets(self, 
        truth: list[Track],
        use_lpf=True,
    ):
        """Synchronizes the raw tile signals with a ground truth (using a search for best fit),
        correcting altitude & time vectors (x&y) with translational offsets.

        Note: this places the time vector in timestamp format, for comparison to ground truth signals.
        """
        logger.info(f'Identifying timestamp and altitude offsets.')

        opt_ts, opt_alt = identifyOffsets(self.raw_alt_lpf if use_lpf else self.raw_alt, use_lpf)
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


    def identifyGeographicalPoints(self=None):
        """Identifies key geographical points of interest, including lift peaks, run peaks, and 
        run bottoms for internal storage and use with other identifications.
        """
        logger.info(f'Identifying key geographical points based on altitude.')

        self.geography = Geography(self.time, self.alt_lpf)
        self.downhill_idxs = np.transpose([
            [el.idx for el in self.geography.run_peaks],
            [el.idx for el in self.geography.run_bottoms],
        ])
        self.lift_idxs = np.transpose([
            [el.idx for el in self.geography.lift_bottoms],
            [el.idx for el in self.geography.lift_peaks],
        ])
        self.peak_idxs = np.transpose([
            [el.idx for el in self.geography.lift_peaks],
            [el.idx for el in self.geography.run_peaks],
        ])


    def identifyJumps(self=None):
        """Identify all points of low G-force and run the jump id pipeline on each.
        
        Confidence values will be associated with each `Jump` instance.
        """
        logger.info(f'Identifying key points of near-zero acceleration.')
        lowG_els = identifyLTThInsideRanges(self.g_force.mG_lpf, JUMP_THRESHOLD_MG, self.downhill_idxs)

        logger.info(f'Identifying jumping kinematics.')
        self.jumps = [
            Jump(lowG_els[row], self.g_force, self.gyro_v)
            for row in range(lowG_els.shape[0])
        ]


    def identifyStaticRegistrations(self=None):
        """Identifies points for static sensor tile boot registrations, seen as the motionless 
        lift peaks after the moment of landing.

        Store with an attached timestamp, so that the system computes boot orientations based on new
        registrations (if any pass the tests!)
        """
        logger.info(f'Identifying static registrations at lift peaks.')

        self.static_registration = StaticRegistration(
            peak_idxs=self.peak_idxs,
            time=self.time,
            alt_lpf=self.alt_lpf,
            mG=self.g_force.mG,
            imu=self.imu,
        )


    def identifyDynamicResitrations(self):
        """Identifies points for dynamic sensor tile boot registrations, seen as the moments of low
        g-forces during turning, where the ski is estimated to be flat.

        Store with an attached timestamp, so that the system computes boot orientations based on new
        registrations (if any pass the tests!)

        May not need, since the ski angles are computed wrt to a baseline. Unless, you need the baselines
        elsewhere!
        """


    def computeBootOrientations(self=None):
        """Based on the identified static registrations, sensor orientations are transformed into the boot frame.
        
        Since registrations update and contain an associated timestamp, the boot orientations will update whenever
        this happens. Ideally, static registrations would occur at the top of every lift and correct orientations
        on that frequency- otherwise this method will use the most recent registration available for sensor to boot
        orientation transformations.
        """
        logger.info(f'Converting orientation into static boot frame.')
        self.boot_quat = np.apply_along_axis(convertToBootFrame, 1, self.imu.quat)

        # center the boot orientation
        logger.info(f'Applying static registations to compute the orientation quaternion representing the boot.')
        for i in range(self.boot_quat.shape[0] - 1):
            self.boot_quat[i] = quatMult(
                self.boot_quat[i], 
                self.static_registration.getMostRecentRegistrationQuat(self.time[i])
            )

        logger.debug('Converting boot orientation into euler data.')
        self.boot_euler = np.apply_along_axis(quatToEuler, 1, self.boot_quat)


    def identifyTurns(self=None):
        """Identify all turn-based kinematics."""
        logger.info(f'Identifying key points of larger acceleration.')
        highG_els = zeroCrossingIdxsGTThInsideRanges(self.g_force.d_mG_lpf_dt, D_MG_LPF_DT_TH, self.downhill_idxs)

        logger.info(f'Identifying turning kinematics based on large accelerations.')
        self.turns = [
            Turn(highG_els[idx], self.alt_lpf, self.g_force, self.boot_euler)
            for idx in range(highG_els.shape[0])
        ]


    @property
    def time(self) -> np.ndarray:
        """Time vector, in `s`. [Nx1]"""
        return self.__time
    
    @time.setter
    def time(self, time):
        self.__time = time


    @property
    def raw_alt(self) -> np.ndarray:
        """Converts the pressure data in mB to altitude in m, using:
        https://www.weather.gov/media/epz/wxcalc/pressureAltitude.pdf.

        Will still need to account for (relatively constant) weather offsets!
        [Nx1]
        """
        return self.__raw_alt
    
    @raw_alt.setter
    def raw_alt(self, raw_alt):
        self.__raw_alt = raw_alt


    @property
    def raw_alt_lpf(self) -> np.ndarray:
        """Filtered raw (no offset) altitude signal with a 2nd order 1/100 LP butterworth filter. [Nx1]"""
        return self.__raw_alt_lpf

    @raw_alt_lpf.setter
    def raw_alt_lpf(self, raw_alt_lpf):
        self.__raw_alt_lpf = raw_alt_lpf


    @property
    def alt(self) -> np.ndarray:
        """Offset altitude signal based on ground truth and is set inside `sync()`. [Nx1]"""
        return self.__alt
    
    @alt.setter
    def alt(self, alt):
        self.__alt = alt


    @property
    def alt_lpf(self) -> np.ndarray:
        """Filtered offset altitude signal with a 2nd order 1/100 LP butterworth filter. [Nx1]"""
        return self.__alt_lpf

    @alt_lpf.setter
    def alt_lpf(self, alt_lpf):
        self.__alt_lpf = alt_lpf


    @property
    def gyro_v(self) -> np.ndarray:
        """Unfiltered 3D gyroscopic vector magnitude.  [Nx1]"""
        return self.__gyro_v
    
    @gyro_v.setter
    def gyro_v(self, gyro_v):
        self.__gyro_v = gyro_v


    @property
    def imu(self) -> IMU:
        """6/9dof based orientation, default 6dof unless overriden via `init(prefer_9dof)`. Euler: [Nx3], Quat: [Nx4]"""
        return self.__imu
    
    @imu.setter
    def imu(self, imu):
        self.__imu = imu
        
        
    @property
    def g_force(self) -> GForce:
        """G force object containing the filtered, derivative, and raw norm signals."""
        return self.__g_force

    @g_force.setter
    def g_force(self, g_force):
        self.__g_force = g_force


    @property
    def geography(self) -> Geography:
        """Key geographical moments/points of interest."""
        return self.__geography
    
    @geography.setter
    def geography(self, geography):
        self.__geography = geography
        

    @property
    def downhill_idxs(self) -> np.ndarray:
        return self.__downhill_idxs
    
    @downhill_idxs.setter
    def downhill_idxs(self, downhill_idxs):
        self.__downhill_idxs = downhill_idxs
        

    @property
    def lift_idxs(self) -> np.ndarray:
        return self.__lift_idxs
    
    @lift_idxs.setter
    def lift_idxs(self, lift_idxs):
        self.__lift_idxs = lift_idxs
        

    @property
    def peak_idxs(self) -> np.ndarray:
        return self.__peak_idxs
    
    @peak_idxs.setter
    def peak_idxs(self, peak_idxs):
        self.__peak_idxs = peak_idxs
        

    @property
    def bottom_idxs(self) -> np.ndarray:
        return self.__bottom_idxs
    
    @bottom_idxs.setter
    def bottom_idxs(self, bottom_idxs):
        self.__bottom_idxs = bottom_idxs
        

    @property
    def jumps(self) -> list[Jump]:
        """Jumps identified from kinematic analysis, includes analytics inside the internal `Jump` objects."""
        return self.__jumps
    
    @jumps.setter
    def jumps(self, jumps):
        self.__jumps = jumps


    @property
    def static_registration(self) -> StaticRegistration:
        """Registration for sensor to boot frame rotations. [1x4]"""
        return self.__static_registration
    
    @static_registration.setter
    def static_registration(self, static_registration):
        self.__static_registration = static_registration
        

    @property
    def boot_quat(self) -> np.ndarray:
        """Boot orientation quaternion [Nx4] (rotation) transformed from the sensor orientation and latest 
        available static registration from lift peaks. Using the dof based orientation signals.
        """
        return self.__boot_rot
    
    @boot_quat.setter
    def boot_quat(self, boot_rot):
        self.__boot_rot = boot_rot


    @property
    def turns(self) -> list[Turn]:
        """Turns identified from kinematic analysis, includes analytics inside the internal `Turn` objects."""
        return self.__turns
    
    @turns.setter
    def turns(self, turns):
        self.__turns = turns

