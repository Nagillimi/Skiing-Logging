class Tile:
    def __init__(
            self,
            time,
            ax, ay, az,
            gx, gy, gz,
            mx, my, mz,
            pres,
            temp,
            hum):
        self.time = time
        self.ax = ax
        self.ay = ay
        self.az = az
        self.gx = gx
        self.gy = gy
        self.gz = gz
        self.mx = mx
        self.my = my
        self.mz = mz
        self.pres = pres
        self.temp = temp
        self.hum = hum