import numpy as np
import math

def avgQuat(quats: np.ndarray, weights=None):
    """Performs the calculation for the average quaternion, based on the range `r` provided.
    
    Assumes equal weighting between all the quaternions, otherwise override `weights` list.

    Returns
    -------
    Average orientation quaternion [w, x, y, z] over range `r`.
    """
    N = quats.shape[0]
    ws = np.ones(N) if weights is None else weights
    qavg = np.array([0., 0., 0., 0.])
    for i in range(N):
        # ensure each quat is normalized
        quat = quats[i] / np.linalg.norm(quats[i])

        # flip, account for double cross over
        if i > 0 and quat.dot(quats[0]) < 0.:
            ws[i] -= 1

        qavg = np.add(qavg, quat * ws[i])
    norm = np.linalg.norm(qavg)
    qavg /= norm if not norm == 0 else 1
    return qavg


def createMisalignmentMatrix(alpha = 0, beta = 0, gamma = 0):
    """Creates misalignment matrix given alpha, beta, and gamma angles. Converts a coordinate system
    into a new reference given these rotations. 

    Note: Assumes orthogonal triaxial CS.
    """
    return np.array([
        [1, -gamma, beta],
        [gamma, 1, -alpha],
        [-beta, alpha, 1],
    ])


def eulerToQuat(rpy: np.ndarray) -> np.ndarray:
    """Convert Euler data into an orientation quaternion. Follows a cardan ZYX sequence.

    https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles#Euler_angles_(in_3-2-1_sequence)_to_quaternion_conversion
    """
    halfR = np.deg2rad(rpy[0]) * 0.5
    halfP = np.deg2rad(rpy[1]) * 0.5
    halfY = np.deg2rad(rpy[2]) * 0.5
    cr = math.cos(halfR); cp = math.cos(halfP); cy = math.cos(halfY)
    sr = math.sin(halfR); sp = math.sin(halfP); sy = math.sin(halfY)

    return np.array([
        cr * cp * cy + sr * sp * sy,
        sr * cp * cy - cr * sp * sy,
        cr * sp * cy + sr * cp * sy,
        cr * cp * sy - sr * sp * cy,
    ])


def inverseQuat(q: np.ndarray) -> np.ndarray:
    return np.multiply(q, [1, -1, -1, -1])


def quatToEuler(q: np.ndarray):
    """Converts an orientation quaternion into euler angles, in degrees.
    
    Employs the atan2 method straight from wiki, following a cardan ZYX sequence.
    """
    q = q / np.linalg.norm(q)
    qw = q[0]; qx = q[1]; qy = q[2]; qz = q[3]
    
    # v1
    # https://github.com/xioTechnologies/Fusion/blob/58f9d2e01be0fcda37ebb1af35c7fc09a5dcbeff/Fusion/FusionMath.h#L466
    
    # halfMinusQy2 = 0.5 - qy**2
    # return np.array([
    #     np.rad2deg(np.arctan2(qw*qx + qy*qz, halfMinusQy2 - qx**2)),
    #     np.rad2deg(np.arcsin(2*(qw*qy - qz*qx))),
    #     np.rad2deg(np.arctan2(qw*qz + qx*qy, halfMinusQy2 - qz**2)),
    # ])

    # v2
    # https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles#Quaternion_to_Euler_angles_(in_3-2-1_sequence)_conversion

    # roll (x-axis rotation)
    sinr_cosp = 2 * (qw * qx + qy * qz)
    cosr_cosp = 1 - 2 * (qx * qx + qy * qy)
    roll = np.degrees(np.arctan2(sinr_cosp, cosr_cosp))

    # pitch (y-axis rotation)
    sinp = np.sqrt(1 + 2 * (qw * qy - qx * qz))
    cosp = np.sqrt(1 - 2 * (qw * qy - qx * qz))
    pitch = np.degrees(2 * np.arctan2(sinp, cosp) - np.pi / 2)

    # yaw (z-axis rotation)
    siny_cosp = 2 * (qw * qz + qx * qy)
    cosy_cosp = 1 - 2 * (qy * qy + qz * qz)
    yaw = np.degrees(np.arctan2(siny_cosp, cosy_cosp))

    return np.array([roll, pitch, yaw])


def quatMult(qa: np.ndarray, qb: np.ndarray) -> np.ndarray:
    """Multiplies 2 quaternions via the hamilton product. Directly mutliplying a quaternion
    without the matching inverse performs a vector rotation.
    
    For quaternion rotations with the
    inverse, use `quatRot()`.
    """
    qa_w = qa[0]; qa_x = qa[1]; qa_y = qa[2]; qa_z = qa[3]
    qb_w = qb[0]; qb_x = qb[1]; qb_y = qb[2]; qb_z = qb[3]

    return np.array([
        qa_w*qb_w - qa_x*qb_x - qa_y*qb_y - qa_z*qb_z,  # w
        qa_w*qb_x + qa_x*qb_w + qa_y*qb_z - qa_z*qb_y,  # x
        qa_w*qb_y - qa_x*qb_z + qa_y*qb_w + qa_z*qb_x,  # y
        qa_w*qb_z + qa_x*qb_y - qa_y*qb_x + qa_z*qb_w,  # z
    ])


def quatRot(q_input: np.ndarray, q_rot: np.ndarray, inverse=False) -> np.ndarray:
    r"""Applies a rotation on quaterion `q_input` by `q_rot`. Useful for converting a CS reference.
    
    Follows the convention:
    .. math::

    q_{result} = q_{rot} \cdot q_{i} \cdot q_{rot}^{-1}
    """
    # q_input = q_input / np.linalg.norm(q_input)
    q_rot = q_rot / np.linalg.norm(q_rot)
    q_rot_i = inverseQuat(q_rot)
    return (
        quatMult(quatMult(q_rot, q_input), q_rot_i) 
        if inverse is False else
        quatMult(quatMult(q_rot_i, q_input), q_rot)
    )