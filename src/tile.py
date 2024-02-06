from jump import JUMP_THRESHOLD_MG, Jump
from raw_tile import RawTile
from registration import Registration
from static_registration import StaticRegistration
import stitch
from imu import IMU
from sig_proc_np import identifyRangesBelowTH, length, lowpass, lowpass
import numpy as np
from track import Track

class Tile:
    def __init__(
            self,
            raw: RawTile,
            print_out=False,
    ):
        self.time = raw.time
        self.constructProcessedSignals(raw, print_out=print_out)


    def __printProps__(self, prefix="\t"):
        in_s = self.time[1] - self.time[0] <= 0.01
        print(
            prefix,
            "Duration [s]", round((self.time[-1] - self.time[0]) / (1 if in_s else 1000))
        )


    def constructProcessedSignals(self, raw: RawTile, print_out=False):
        """Constructs all the processed signals for the Tile sensor."""
        self.raw_alt = 44307.694 * (1 - (raw.pres / 1013.25)**0.190284)
        self.raw_alt_lpf = lowpass(self.raw_alt, 1/100, 'butter2')
        self.gyro_v = length(raw.gyro)
        self.mG = length(raw.accel)

        self.accel_lpf = lowpass(raw.accel, 3/100, 'butter2')
        self.mG_lpf = length(self.accel_lpf)

        self.imu6 = IMU(raw.accel, raw.gyro, print_out=print_out)
        self.imu9 = IMU(raw.accel, raw.gyro, raw.mag, print_out=print_out)


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
        tile_alt = self.raw_alt_lpf if use_lpf else self.raw_alt
        stitched_a50_time, stitched_a50_alt = stitch(truth)

        # 2. find the optimal time and altitude offsets
        shift_h_tile = []; shift_v_tile = []
        collection = []
        tile_ts_search = 0
        for i in range(max_time_search_s):
            # horizontal shift & downsample to 1Hz (for truth comparison)
            shift_h_tile = tile_alt[tile_ts_search : (tile_ts_search + len(stitched_a50_time) * 100) : 100]

            # reset the elevation starting point
            tile_alt_search = min_alt_start
            for _ in range(round(max_alt_search / alt_step)):
                # vertical shift
                shift_v_tile = shift_h_tile - tile_alt_search

                # calculate the mae, sse
                d = shift_v_tile - stitched_a50_alt
                abs_d = np.abs(d)
                d2 = d**2
                mae = np.mean(abs_d)
                mse = np.mean(d2)

                # append to lists
                collection.append([tile_ts_search, tile_alt_search, mae, mse])

                # iterate
                tile_alt_search += alt_step

            # iterate (in seconds)
            tile_ts_search += int(time_step_s * 1000)
            if print_progress:
                progress = round(100 * (i + 1) / (max_time_search_s + 1))
                print(progress, '%', sep="")
        
        ts_all = [m[0] for m in collection]
        alt_all = [m[1] for m in collection]
        mae_all = [m[2] for m in collection]
        mse_all = [m[3] for m in collection]
        min_ts_idx = 0
        if use_mae: min_ts_idx = mae_all.index(min(mae_all))
        else: min_ts_idx = mse_all.index(min(mse_all))

        # 3. Align the timestamp with the start of the a50 dataset, incorporating the offset
        opt_ts = ts_all[min_ts_idx] 
        opt_alt = alt_all[min_ts_idx]
        if print_out:
            print('Synchronized Tile Parameters')
            print('\tTimestamp offset (ms):', opt_ts)
            print('\tAltitude offset (m):', opt_alt)

        self.applyOffsets(opt_ts, opt_alt)
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
        static_reg6 = StaticRegistration(self.time, self.alt_lpf, self.mG, self.imu6, print_out)
        static_reg9 = StaticRegistration(self.time, self.alt_lpf, self.mG, self.imu9, print_out)
        self.qSB_6 = static_reg6.registrations
        self.qSB_9 = static_reg9.registrations


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
    def qSB_6(self) -> list[Registration]:
        """Registration for sensor to boot frame rotations, based on 6dof. [1x4]"""
        return self.__qSB_6
    
    @qSB_6.setter
    def qSB_6(self, qsb6):
        self.__qSB_6 = qsb6
        
    
    @property
    def qSB_9(self) -> list[Registration]:
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
    def jumps(self, js):
        self.__jumps = js
