import numpy as np

class Registration:
    def __init__(
            self,
            ts: float,
            range: list[int],
            avg_quat: np.ndarray
    ) -> None:
        self.ts = ts
        self.range = range
        self.avg_quat = avg_quat


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