import numpy as np

class RawTile:
    def __init__(
            self,
            time: np.ndarray,
            accel: np.ndarray,
            gyro: np.ndarray,
            mag: np.ndarray,
            pres: np.ndarray,
            temp: np.ndarray,
            hum: np.ndarray,
    ) -> None:
        self.time = time
        """Time vector, in `ms`. [Nx1]"""
        
        self.accel = accel
        """Triaxial accelerometer signals, in `mG`. [Nx3]"""
        
        self.gyro = gyro
        """Triaxial gyroscope signals, in `mdps`. [Nx3]"""
        
        self.mag = mag
        """Triaxial magnetometer signals, in `mGauss`. [Nx3]"""
        
        self.pres = pres
        """Air pressure measurements, in `mB`. [Nx1]"""
        
        self.temp = temp
        """Temperature measurements, in `degC`. [Nx1]"""
        
        self.hum = hum
        """Relative humidity measurements, in `%`. [Nx1]"""
        