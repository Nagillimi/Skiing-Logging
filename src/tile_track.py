from datetime import date, time
from io import TextIOWrapper
from imu import IMU
from datafile import constructJumpLine
# from tile import Tile
from jump import Jump, JUMP_THRESHOLD_MG
from sig_proc import identifyRangesBelowTH, makeContinuousRange3dof
import numpy as np

class TileTrack:
    """TileTrack sublcass of Tile, acting as protocol inheritance.
    Do NOT call super here, props and methods are overridden in all intersecting cases.


    """
    def __init__(
            self,
            parent_tile,
            range: list,
            file_train: TextIOWrapper,
            track_type='Downhill',
            identifyKinematics = True,
    ):
        self.track_type = track_type
        self.time = parent_tile.time[range[0]:range[1]]
        self.ax = parent_tile.ax[range[0]:range[1]]
        self.ay = parent_tile.ay[range[0]:range[1]]
        self.az = parent_tile.az[range[0]:range[1]]
        self.gx = parent_tile.gx[range[0]:range[1]]
        self.gy = parent_tile.gy[range[0]:range[1]]
        self.gz = parent_tile.gz[range[0]:range[1]]
        self.mx = parent_tile.mx[range[0]:range[1]]
        self.my = parent_tile.my[range[0]:range[1]]
        self.mz = parent_tile.mz[range[0]:range[1]]
        self.pres = parent_tile.pres[range[0]:range[1]]
        self.temp = parent_tile.temp[range[0]:range[1]]
        self.hum = parent_tile.hum[range[0]:range[1]]
        self.corrected_alt = parent_tile.corrected_alt[range[0]:range[1]]
        self.imu6 = self.trimIMU(parent_tile.imu6, range)
        self.imu9 = self.trimIMU(parent_tile.imu9, range)
        self.file_train = file_train

        if not identifyKinematics:
            return
        self.identifyJumps()
        self.identifyTurns()


    @property
    def euler6_b(self):
        """Rotated IMU data (basaed on 6dof) put with reference to the boot frame.
        
        Set from the detected still phases at the lift tops.
        """
        print('euler6_b self.qSB6:', self.qSB6)
        return makeContinuousRange3dof(
            np.array([self.imu6.computeEuler(quat=q) for q in self.imu6.tareOrientation(self.qSB6)]),
            fix_0=False,
            fix_1=False,
            fix_2=True,
        )


    @property
    def euler9_b(self):
        """Rotated IMU data (basaed on 9dof) put with reference to the boot frame.
        
        Set from the detected still phases at the lift tops.
        """
        return makeContinuousRange3dof(
            np.array([self.imu9.computeEuler(quat=q) for q in self.imu9.tareOrientation(self.qSB9)]),
            fix_0=False,
            fix_1=False,
            fix_2=True,
        )


    def trimIMU(self, imu: IMU, r):
        """Trims the existing orientation signals from the parent tile object.
        
        Doesn't recompute the orientation data based on trimmed motion data since it'd consume
        more processing, 
        """
        print('trimming IMU:', imu, 'to range:', r)
        return IMU([], [], quat=imu.quat[r[0]:r[1], :])


    def logJumpData(self, override_th=None):
        for jump in self.jumps:
            self.file_train.write(constructJumpLine(jump))


    def identifyJumps(self, override_th=None):
        """Identify all points of low G-force and run the jump id pipeline on each.
        
        Confidence values will be associated with each `Jump` instance.
        """
        lowG_els = identifyRangesBelowTH(
            self.mG_lpf(),
            JUMP_THRESHOLD_MG if override_th is None else override_th
        )
        self.jumps = [Jump(el, self.mG_lpf(), self.mG, self.gyro) for el in lowG_els]
        self.logJumpData(override_th)

    
    def identifyTurns(self): pass

