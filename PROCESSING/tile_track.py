from datetime import date, time
from tile import Tile
from track import Track
from jump import Jump
from signal_processing import identifyRangesBelowTH, length, lowpass

class TileTrack(Tile):
    def __init__(
            self,
            track_type: str,
            date: date,
            tod: time,
            duration: int,
            length: int,
            time: list[float],
            ax: list[int], ay: list[int], az: list[int],
            gx: list[int], gy: list[int], gz: list[int],
            mx: list[int], my: list[int], mz: list[int],
            pres: list[float],
            temp: list[float],
            hum: list[float],
            corrected_alt: list[float],
            identifyKinematics=True
    ):
        super().__init__(
            time=time,
            ax=ax, ay=ay, az=az,
            gx=gx, gy=gy, gz=gz,
            mx=mx, my=my, mz=mz,
            pres=pres,
            temp=temp,
            hum=hum,
            corrected_alt=corrected_alt
        )
        # set track metadata from the parent a50 track
        self.track = Track(
            track_type=track_type,
            date=date,
            tod=tod,
            duration=duration,
            length=length,
            time=time,
            dist=[], vel=[], alt=[], lat=[], long=[]
        )
        if not identifyKinematics:
            return
        self.identifyJumps()
        self.identifyTurns()


    def __printProps__(self, prefix="\t"):
        return self.track.__printProps__(prefix)


    def identifyJumps(self):
        """Identify all points of low G-force and run the jump id pipeline on each.
        
        Confidence values will be associated with each `Jump` instance.
        """
        lowG_els = identifyRangesBelowTH(self.mG_lpf(), Jump.mGThreshold())
        self.jumps = [Jump(el, self.mG_lpf(), self.mG, self.gyro) for el in lowG_els]

    
    def identifyTurns(self): pass

