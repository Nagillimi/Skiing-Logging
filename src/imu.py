import imufusion
import numpy as np
from quat import quatMult, quatToEuler
from signal_processing import makeContinuousRange3dof
import math 

class IMU:
    """
    Class to contain all the IMU logic and methods for conversion to euler data.
    """

    def __init__(
            self,
            accel: np.ndarray,
            gyro: np.ndarray,
            mag: np.ndarray = None,
            fs=100,
            gain = 0.5,
            gyro_range=2000,
            accel_reject=10,
            mag_reject=10,
            recovery_period_s=5,
            quat=None,
        ) -> None:
        """Initializes the IMU object and performs the orientation calculations based on the amount
        of data sent (6dof for accel/gyro, 9dof  +mag).
        
        Assumes the motion data is passed in how the Tile is parsed, in [3xN] matrix shape. Sample 
        rate is set to 100Hz, override `fs` otherwise.
        """
        
        self.offset = imufusion.Offset(fs)
        self.ahrs = imufusion.Ahrs()
        self.fs = fs
        self.accel = np.divide(accel, 1000)
        """Accelerometer data converted to G's."""

        self.gyro = np.divide(gyro, 1000)
        """Gyroscope data converted to dps."""

        self.mag = np.divide(mag, 10) if mag is not None else None
        """Magnetometer data converted to uT."""

        self.ahrs.settings = imufusion.Settings(
            imufusion.CONVENTION_NWU,
            gain,
            gyro_range,
            accel_reject,
            mag_reject,
            recovery_period_s * fs,
        )

        self.quat = self.computeOrientation() if quat is None else quat
        """Quaternion dataset, convention [w,x,y,z]."""

        self.euler = self.computeEuler(quat=None if quat is None else quat)
        """Euler data based on the orientation quaternion, yaw is by default unclamped.
        
        If you want clamped yaw data, use `getClampedEuler()`
        """

        self.euler_norm = [np.linalg.norm(self.euler[row, :]) for row in range(self.euler.shape[0])]
        """
        Vector norm of the euler data to represent a single combined angle, in 3D.
        Assumed the yaw angle is best in cts range, useful for motion tests & calculations.
        """


    def computeOrientation(self):
        """Compute the orientation quaternion with the motion data.
        
        Computes either 6 or 9dof based depending on whether the mag was set.
        """
        quat = np.empty((self.accel.shape[0], 4))
        for i in range(self.accel.shape[0]):
            offset_gyro = self.offset.update(self.gyro[i])
            if self.mag is None:
                self.ahrs.update_no_magnetometer(offset_gyro, self.accel[i], 1 / self.fs)
            else:
                self.ahrs.update(offset_gyro, self.accel[i], self.mag[i], 1 / self.fs)
            q = self.ahrs.quaternion
            quat[i] = [q.w, q.x, q.y, q.z]
        return quat
    

    # https://github.com/xioTechnologies/Fusion/blob/58f9d2e01be0fcda37ebb1af35c7fc09a5dcbeff/Fusion/FusionMath.h#L466
    def computeEuler(self, cts_yaw=True, quat=None):
        """Gets the euler data from the orientatio quaternion, 
        assuming yaw data in a continuous range otherwise set `cts_yaw` to False."""
        euler = np.empty((self.quat.shape[0], 3))
        for i in range(self.quat.shape[0]):
            euler[i] = quatToEuler(self.quat[i])
        return makeContinuousRange3dof(
            euler,
            fix_0=False,
            fix_1=False,
            fix_2=cts_yaw,
        )


    def tareOrientation(self, qSB):
        """Rotates the orientation data by a quaternion [w, x, y, z].
        
        `qSB` for converting from "sensor to boot frame".
        """
        qSB_i = np.multiply(qSB, [1, -1, -1, -1])
        return [quatMult(quatMult(qSB, q), qSB_i) for q in self.quat]
    
