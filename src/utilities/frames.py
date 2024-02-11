import numpy as np
from utilities.quat import eulerToQuat, quatRot


def convertToBootFrame(q: np.ndarray) -> np.ndarray:
    """Converts the input quaternion in sensor frame to boot frame.
    
    Using the static definition of, on right boot:
        - `x` forwards
        - `y` right
        - `z` down
    """
    q_rot = eulerToQuat(np.array([0, 180, -90]))
    return quatRot(q, q_rot, True)