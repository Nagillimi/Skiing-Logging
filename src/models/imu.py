import imufusion
import numpy as np
from domain.session_logger import SessionLogger as logger
from utilities.quat import quatToEuler
from utilities.sig_proc_np import makeContinuousRange3dof

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
        ) -> None:
        """Initializes the IMU object and performs the orientation calculations based on the amount
        of data sent (6dof for accel/gyro, 9dof  +mag).
        
        Assumes the motion data is passed in how the Tile is parsed, in [3xN] matrix shape. Sample 
        rate is set to 100Hz, override `fs` otherwise.
        """
        # convert data to G's, dps, & uT
        a = accel / 1000
        g = gyro / 1000
        m = mag / 10 if mag is not None else None

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
        self.computeOrientation(a, g, m)
        self.computeEuler()


    def convertToBootFrame(self, x: np.ndarray) -> np.ndarray:
        return np.transpose([x[:, 1], -x[:, 2], -x[:, 0]])


    def computeOrientation(self, a: np.ndarray, g: np.ndarray, m=None):
        """Compute the orientation quaternion with the motion data.
        
        Computes either 6 or 9dof based depending on whether the mag was set.
        """
        N = a.shape[0]
        self.quat = np.empty((N, 4))
        logger.debug(f'Computing orientation for {self}')

        for i in range(N):
            g[i] = self.offset.update(g[i])
            if m is None:
                self.ahrs.update_no_magnetometer(g[i], a[i], 1 / self.fs)
            else:
                self.ahrs.update(g[i], a[i], m[i], 1 / self.fs)
            q = self.ahrs.quaternion
            self.quat[i] = [q.w, q.x, q.y, q.z]
    

    def computeEuler(self):
        """Computes the clamped euler data based on the orientation quaternion in the sensor frame.

        Also computes the euler norm (based on clamped signals), for external algorithm use.
        """
        logger.debug(f'Translating orientation into euler data for {self}')
        self.euler = np.apply_along_axis(quatToEuler, 1, self.quat)
        self.euler_combined = np.linalg.norm(self.euler, axis=1)


    @property
    def cts_euler(self) -> np.ndarray:
        """Continuous (unclamped) euler data based on the orientation quaternion. No attached setter,
        since this is assumed to only be used in prototyping situation and will be deprecated.
        
        `** Watch out- this getter is inherently very slow! **`
        """
        return makeContinuousRange3dof(self.euler, debug_file=True)
    

    @property
    def euler(self) -> np.ndarray:
        """Euler data based on the orientation quaternion, clamped.
        
        If you want clamped yaw data, use `cts_euler`
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

