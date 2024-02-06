import imufusion
import numpy as np
from quat import quatMult, quatToEuler
from sig_proc_np import makeContinuousRange3dof

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
            print_out=False,
        ) -> None:
        """Initializes the IMU object and performs the orientation calculations based on the amount
        of data sent (6dof for accel/gyro, 9dof  +mag).
        
        Assumes the motion data is passed in how the Tile is parsed, in [3xN] matrix shape. Sample 
        rate is set to 100Hz, override `fs` otherwise.
        """
        # convert data to G's, dps, & uT
        a = np.divide(accel, 1000)
        g = np.divide(gyro, 1000)
        m = np.divide(mag, 10) if mag is not None else None

        self.offset = imufusion.Offset(fs)
        self.ahrs = imufusion.Ahrs()
        self.fs = fs
        self.ahrs.settings = imufusion.Settings(
            imufusion.CONVENTION_NWU,
            gain,
            gyro_range,
            accel_reject,
            mag_reject,
            recovery_period_s * fs,
        )
        self.computeOrientation(a, g, m, print_out=print_out)
        self.computeEuler(print_out=print_out)


    def computeOrientation(self, a: np.ndarray, g: np.ndarray, m=None, print_out=False):
        """Compute the orientation quaternion with the motion data.
        
        Computes either 6 or 9dof based depending on whether the mag was set.
        """
        N = a.shape[0]
        self.quat = np.empty((N, 4))
        if print_out: print('Computing orientation for', self)

        for i in range(N):
            offset_gyro = self.offset.update(g[i])
            if m is None:
                self.ahrs.update_no_magnetometer(offset_gyro, a[i], 1 / self.fs)
            else:
                self.ahrs.update(offset_gyro, a[i], m[i], 1 / self.fs)
            q = self.ahrs.quaternion
            self.quat[i] = [q.w, q.x, q.y, q.z]
    

    # https://github.com/xioTechnologies/Fusion/blob/58f9d2e01be0fcda37ebb1af35c7fc09a5dcbeff/Fusion/FusionMath.h#L466
    def computeEuler(self, cts_yaw=True, print_out=False):
        """Gets the euler data from the orientatio quaternion, 
        assuming yaw data in a continuous range otherwise set `cts_yaw` to False.
        """
        if print_out: print('Translating orientation into euler data for', self)
        euler = np.apply_along_axis(quatToEuler, 1, self.quat)
        self.euler_combined = np.linalg.norm(euler, axis=1)
        self.euler = makeContinuousRange3dof(
            euler,
            fix_0=True,
            fix_1=False,
            fix_2=cts_yaw,
            print_out=print_out
        )
        if print_out: print('Converted euler data into continuous range.')


    def tareOrientation(self, qSB):
        """Rotates the orientation data by a quaternion [w, x, y, z].
        
        `qSB` for converting from "sensor to boot frame".
        """
        qSB_i = np.multiply(qSB, [1, -1, -1, -1])
        return [quatMult(quatMult(qSB, q), qSB_i) for q in self.quat]
    

    @property
    def euler(self) -> np.ndarray:
        """Euler data based on the orientation quaternion, yaw is by default unclamped.
        
        If you want clamped yaw data, use `getClampedEuler()`
        """
        return self.__euler
    
    @euler.setter
    def euler(self, e):
        self.__euler = e
        

    @property
    def euler_combined(self) -> np.ndarray:
        """
        Vector norm of the euler data to represent a single combined angle, in 3D.
        Assumed the yaw angle is best in cts range, useful for motion tests & calculations.
        """
        return self.__euler_combined
    
    @euler_combined.setter
    def euler_combined(self, e):
        self.__euler_combined = e
        

    @property
    def quat(self) -> np.ndarray:
        """Quaternion dataset, convention [w,x,y,z]."""
        return self.__quat
    
    @quat.setter
    def quat(self, e):
        self.__quat = e

