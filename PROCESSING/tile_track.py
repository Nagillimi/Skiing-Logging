from datetime import date, time
from io import TextIOWrapper
from datafile import constructJumpLine
from tile import Tile
from track import Track
from jump import Jump, JUMP_THRESHOLD_MG
from signal_processing import identifyRangesBelowTH
import numpy as np

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
            file_train: TextIOWrapper,
            identifyKinematics=True,
            euler6=None,
            euler9=None,
    ):
        super().__init__(
            time=time,
            ax=ax, ay=ay, az=az,
            gx=gx, gy=gy, gz=gz,
            mx=mx, my=my, mz=mz,
            pres=pres,
            temp=temp,
            hum=hum,
            corrected_alt=corrected_alt,
            euler6=euler6, euler9=euler9
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
        self.file_train = file_train
        if not identifyKinematics:
            return
        self.identifyJumps()
        self.identifyTurns()


    def __printProps__(self, prefix="\t"):
        return self.track.__printProps__(prefix)


    def logJumpData(self, override_th=None):
        for jump in self.jumps:
            self.file_train.write(constructJumpLine(jump))


    def identifyJumps(self, override_th=None):
        """Identify all points of low G-force and run the jump id pipeline on each.
        
        Confidence values will be associated with each `Jump` instance.
        """
        lowG_els = identifyRangesBelowTH(
            self.mG_lpf(),
            JUMP_THRESHOLD_MG if override_th is None else override_th
        )
        self.jumps = [Jump(el, self.mG_lpf(), self.mG, self.gyro) for el in lowG_els]
        self.logJumpData(override_th)

    
    def identifyTurns(self): pass

