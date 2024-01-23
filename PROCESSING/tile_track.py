from datetime import date, time
from io import TextIOWrapper
from imu import IMU
from datafile import constructJumpLine
from tile import Tile
from track import Track
from jump import Jump, JUMP_THRESHOLD_MG
from signal_processing import identifyRangesBelowTH, makeContinuousRange3dof
import numpy as np

class TileTrack(Tile):
    def __init__(
            self,
            track_type: str,
            date: date,
            tod: time,
            duration: int,
            length: int,
            parent_tile: Tile,
            range: list,
            file_train: TextIOWrapper,
            identifyKinematics: bool,
    ):
        trimmed_imu6 = self.trimIMU(parent_tile.imu6, range)
        trimmed_imu9 = self.trimIMU(parent_tile.imu9, range)

        super().__init__(
            time=parent_tile.time[range[0]:range[1]],
            ax=parent_tile.ax[range[0]:range[1]],
            ay=parent_tile.ay[range[0]:range[1]],
            az=parent_tile.az[range[0]:range[1]],
            gx=parent_tile.gx[range[0]:range[1]],
            gy=parent_tile.gy[range[0]:range[1]],
            gz=parent_tile.gz[range[0]:range[1]],
            mx=parent_tile.mx[range[0]:range[1]],
            my=parent_tile.my[range[0]:range[1]],
            mz=parent_tile.mz[range[0]:range[1]],
            pres=parent_tile.pres[range[0]:range[1]],
            temp=parent_tile.temp[range[0]:range[1]],
            hum=parent_tile.hum[range[0]:range[1]],
            corrected_alt=parent_tile.corrected_alt[range[0]:range[1]],
            imu6=trimmed_imu6,
            imu9=trimmed_imu9,
        )
        # set track metadata from the parent a50 track
        self.track = Track(
            track_type=track_type,
            date=date,
            tod=tod,
            duration=duration,
            length=length,
            time=time,
            dist=[], vel=[], alt=[], lat=[], long=[]
        )
        self.file_train = file_train
        if not identifyKinematics:
            return
        self.identifyJumps()
        self.identifyTurns()


    def __printProps__(self, prefix="\t"):
        return self.track.__printProps__(prefix)


    @property
    def euler6_b(self):
        """Rotated IMU data (basaed on 6dof) put with reference to the boot frame.
        
        Set from the detected still phases at the lift tops.
        """
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
        trimmedIMU = IMU([], [], run=False)
        trimmedIMU.quat = imu.quat[r[0]:r[1]]
        trimmedIMU.euler = imu.euler[r[0]:r[1], :]
        trimmedIMU.euler_norm = imu.euler_norm[r[0]:r[1]]
        trimmedIMU.accel = imu.accel[r[0]:r[1], :]
        trimmedIMU.gyro = imu.gyro[r[0]:r[1], :]
        trimmedIMU.mag = imu.mag[r[0]:r[1], :] if imu.mag is not None else None
        return trimmedIMU


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

