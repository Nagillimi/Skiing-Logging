import numpy as np
from utilities.sig_proc_np import deriv, length, lowpass


class GForce:
    def __init__(
            self,
            raw_accel: np.ndarray, 
    ) -> None:
        self.mG = length(raw_accel)
        self.accel_lpf = lowpass(raw_accel, 3/100, 'butter2')
        self.mG_lpf = length(self.accel_lpf)
        self.d_mG_lpf_dt = deriv(self.mG_lpf, 0.01)
        self.d2_mG_lpf_dt2 = deriv(self.d_mG_lpf_dt, 0.01)

        
    @property
    def mG(self) -> np.ndarray:
        """Unfiltered mG-forces (3D accelerometer vector magnitude). [Nx1]"""
        return self.__mG

    @mG.setter
    def mG(self, mG):
        self.__mG = mG


    @property
    def accel_lpf(self) -> np.ndarray:
        """Filtered accelerometer signals. [Nx1]"""
        return self.__accel_lpf
    
    @accel_lpf.setter
    def accel_lpf(self, accel_lpf):
        self.__accel_lpf = accel_lpf


    @property
    def mG_lpf(self) -> np.ndarray:
        """Filtered mG-forces. [Nx1]"""
        return self.__mG_lpf
    
    @mG_lpf.setter
    def mG_lpf(self, mG_lpf):
        self.__mG_lpf = mG_lpf
    

    @property
    def d_mG_lpf_dt(self) -> np.ndarray:
        """First derivative of filtered mG-forces. [Nx1]"""
        return self.__d_mG_lpf_dt
    
    @d_mG_lpf_dt.setter
    def d_mG_lpf_dt(self, d_mG_lpf_dt):
        self.__d_mG_lpf_dt = d_mG_lpf_dt
    

    @property
    def d2_mG_lpf_dt2(self) -> np.ndarray:
        """Second derivative of filtered mG-forces. [Nx1]"""
        return self.__d2_mG_lpf_dt2
    
    @d2_mG_lpf_dt2.setter
    def d2_mG_lpf_dt2(self, d2_mG_lpf_dt2):
        self.__d2_mG_lpf_dt2 = d2_mG_lpf_dt2
    
