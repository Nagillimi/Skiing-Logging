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
        self.accel = accel
        self.gyro = gyro
        self.mag = mag
        self.pres = pres
        self.temp = temp
        self.hum = hum


    def __printProps__(self, prefix="\t"):
        print(
            prefix,
            "Track type Variable |",
            "Duration [s]", (self.time[-1] - self.time[0]) / 1000
        )


    @property
    def time(self) -> np.ndarray:
        """Time vector, in `ms`. [Nx1]"""
        return self.__time

    @time.setter
    def time(self, t):
        self.__time = t
        


    @property
    def accel(self) -> np.ndarray:
        """Triaxial accelerometer signals, in `mG`. [Nx3]"""
        return self.__accel

    @accel.setter
    def accel(self, a):
        self.__accel = a


    @property
    def gyro(self) -> np.ndarray:
        """Triaxial gyroscope signals, in `mdps`. [Nx3]"""
        return self.__gyro

    @gyro.setter
    def gyro(self, g):
        self.__gyro = g


    @property
    def mag(self) -> np.ndarray:
        """Triaxial magnetometer signals, in `mGauss`. [Nx3]"""
        return self.__mag

    @mag.setter
    def mag(self, m):
        self.__mag = m


    @property
    def pres(self) -> np.ndarray:
        """Air pressure measurements, in `mB`. [Nx1]"""
        return self.__pres

    @pres.setter
    def pres(self, p):
        self.__pres = p


    @property
    def temp(self) -> np.ndarray:
        """Temperature measurements, in `degC`. [Nx1]"""
        return self.__temp

    @temp.setter
    def temp(self, t):
        self.__temp = t


    @property
    def hum(self) -> np.ndarray:
        """Relative humidity measurements, in `%`. [Nx1]"""
        return self.__hum

    @hum.setter
    def hum(self, h):
        self.__hum = h
