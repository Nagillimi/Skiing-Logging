import numpy as np
from utilities.quat import quatToRotFlatRegistration

class Registration:
    def __init__(
            self,
            ts: float,
            range: list[int],
            avg_quat: np.ndarray,
    ) -> None:
        self.ts = ts
        self.range = range
        self.avg_quat = avg_quat
        self.rp_rotM = quatToRotFlatRegistration(avg_quat)


    @property 
    def ts(self):
        return self.__ts
    
    @ts.setter
    def ts(self, ts):
        self.__ts = ts


    @property 
    def range(self):
        return self.__range
    
    @range.setter
    def range(self, r):
        self.__range = r


    @property 
    def avg_quat(self):
        return self.__avg_quat
    
    @avg_quat.setter
    def avg_quat(self, aq):
        self.__avg_quat = aq


    @property 
    def rp_rotM(self) -> np.ndarray:
        """Roll & Pitch rotation matrix derived from the avg quaternion's euler components.
        
        .. math::

        M = [[1, -1, p], [1, 1, -r], [-p, r, 1]]
        """
        return self.__rp_rotM
    
    @rp_rotM.setter
    def rp_rotM(self, rp):
        self.__rp_rotM = rp