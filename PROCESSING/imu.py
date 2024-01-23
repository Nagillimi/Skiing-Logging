import imufusion
import numpy as np
from quat import quatMult
from signal_processing import makeContinuousRange3dof
import math 

class IMU:
    """
    Class to contain all the IMU logic and methods for conversion to euler data.
    """

    def __init__(
            self,
            accel: list[list],
            gyro: list[list],
            mag: list[list] = None,
            fs=100,
            gain = 0.5,
            gyro_range=2000,
            accel_reject=10,
            mag_reject=10,
            recovery_period_s=5,
            run=True,
        ) -> None:
        """Initializes the IMU object and performs the orientation calculations based on the amount
        of data sent (6dof for accel/gyro, 9dof  +mag).
        
        Assumes the motion data is passed in how the Tile is parsed, in [3xN] matrix shape. Sample 
        rate is set to 100Hz, override `fs` otherwise.
        """
        
        self.offset = imufusion.Offset(fs)
        self.ahrs = imufusion.Ahrs()
        self.fs = fs
        self.accel = np.divide(np.transpose(accel), 1000)
        """Accelerometer data converted to G's."""

        self.gyro = np.divide(np.transpose(gyro), 1000)
        """Gyroscope data converted to dps."""

        self.mag = np.divide(np.transpose(mag), 10) if mag is not None else None
        """Magnetometer data converted to uT."""

        if run is False:
            return
        
        self.ahrs.settings = imufusion.Settings(
            imufusion.CONVENTION_NWU,
            gain,
            gyro_range,
            accel_reject,
            mag_reject,
            recovery_period_s * fs,
        )

        self.quat = self.computeOrientation()
        """Quaternion dataset, convention [w,x,y,z]."""

        self.euler = self.computeEuler()
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
            quat[i] = np.array([q.w, q.x, q.y, q.z])
        return quat
    

    # https://github.com/xioTechnologies/Fusion/blob/58f9d2e01be0fcda37ebb1af35c7fc09a5dcbeff/Fusion/FusionMath.h#L466
    def computeEuler(self, cts_yaw=True, quat=None):
        """Gets the euler data from the orientatio quaternion, 
        assuming yaw data in a continuous range otherwise set `cts_yaw` to False."""
        euler = np.empty((self.accel.shape[0], 3))
        for i, q in enumerate(self.quat if quat is None else quat):
            qw = q[0]; qx = q[1]; qy = q[2]; qz = q[3]
            halfMinusQy2 = 0.5 - qy**2
            euler[i] = [
                math.degrees(math.atan2(qw*qx + qy*qz, halfMinusQy2 - qx**2)),
                math.degrees(math.asin(2*(qw*qy - qz*qx))),
                math.degrees(math.atan2(qw*qz + qx*qy, halfMinusQy2 - qz**2)),
            ]
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
    
        # fml
        # quats = []
        # for q in q_prod:
        #     quat = self.ahrs.quaternion # placeholder until I make my owbn orientation alg
        #     quat.w = q[0]
        #     quat.x = q[1]
        #     quat.y = q[2]
        #     quat.z = q[3]
        #     quats.append(quat)
        # return quats


    def avgQuat(self, r, weights=None):
        """Performs the calculation for the average quaternion, based on the range `r` provided.
        
        Assumes equal weighting between all the quaternions, otherwise override `weights` list.

        Returns
        -------
        Average orientation quaternion [w, x, y, z] over range `r`.
        """
        quats = self.quat[r[0]:r[1], :]
        ws = np.ones(len(quats)) if weights is None else weights
        qavg = np.array([0., 0., 0., 0.])
        for i, quat in enumerate(quats):
            # ensure each quat is normalized
            quat = quat / np.linalg.norm(quat)

            # flip, account for double cross over
            if i > 0 and quat.dot(quats[0]) < 0.:
                print('double cross over!')
                ws[i] -= 1

            qavg = np.add(qavg, quat * ws[i])
        qavg /= np.linalg.norm(qavg)
        print(qavg)
        return qavg / np.linalg.norm(qavg)