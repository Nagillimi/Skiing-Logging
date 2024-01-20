from datetime import date, time
from io import TextIOWrapper
from tile import Tile
from track import Track
from jump import Jump
from signal_processing import identifyRangesBelowTH, mean, std

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
        self.file_train = file_train
        if not identifyKinematics:
            return
        self.identifyJumps()
        self.identifyTurns()


    def __printProps__(self, prefix="\t"):
        return self.track.__printProps__(prefix)


    def logJumpData(self, override_th=None):
        for jump in self.jumps:
            line = f'{Jump.mGThreshold() if override_th is None else override_th},'
            line += f'{jump.lowG_range[0]},'
            line += f'{jump.lowG_range[1]},'
            line += f'{jump.lowG_range[1] - jump.lowG_range[0]},'
            line += f'{jump.mG_lpf[jump.lowG_range[0]] if jump.lowG_range[0] == jump.lowG_range[1] else min(jump.mG_lpf[jump.lowG_range[0]:jump.lowG_range[1]])},'
            line += f'{jump.mG_lpf[jump.lowG_range[0]] if jump.lowG_range[0] == jump.lowG_range[1] else max(jump.mG_lpf[jump.lowG_range[0]:jump.lowG_range[1]])},'
            line += f'{jump.mG_lpf[jump.lowG_range[0]] if jump.lowG_range[0] == jump.lowG_range[1] else mean(jump.mG_lpf[jump.lowG_range[0]:jump.lowG_range[1]])},'
            line += f'{jump.mG_lpf[jump.lowG_range[0]] if jump.lowG_range[0] == jump.lowG_range[1] else std(jump.mG_lpf[jump.lowG_range[0]:jump.lowG_range[1]])},'
            line += f'{jump.mG[jump.lowG_range[0]] if jump.lowG_range[0] == jump.lowG_range[1] else min(jump.mG[jump.lowG_range[0]:jump.lowG_range[1]])},'
            line += f'{jump.mG[jump.lowG_range[0]] if jump.lowG_range[0] == jump.lowG_range[1] else max(jump.mG[jump.lowG_range[0]:jump.lowG_range[1]])},'
            line += f'{jump.mG[jump.lowG_range[0]] if jump.lowG_range[0] == jump.lowG_range[1] else mean(jump.mG[jump.lowG_range[0]:jump.lowG_range[1]])},'
            line += f'{jump.mG[jump.lowG_range[0]] if jump.lowG_range[0] == jump.lowG_range[1] else std(jump.mG[jump.lowG_range[0]:jump.lowG_range[1]])},'
            line += f'{jump.gyro[jump.lowG_range[0]] if jump.lowG_range[0] == jump.lowG_range[1] else min(jump.gyro[jump.lowG_range[0]:jump.lowG_range[1]])},'
            line += f'{jump.gyro[jump.lowG_range[0]] if jump.lowG_range[0] == jump.lowG_range[1] else max(jump.gyro[jump.lowG_range[0]:jump.lowG_range[1]])},'
            line += f'{jump.gyro[jump.lowG_range[0]] if jump.lowG_range[0] == jump.lowG_range[1] else mean(jump.gyro[jump.lowG_range[0]:jump.lowG_range[1]])},'
            line += f'{jump.gyro[jump.lowG_range[0]] if jump.lowG_range[0] == jump.lowG_range[1] else std(jump.gyro[jump.lowG_range[0]:jump.lowG_range[1]])},'
            line += f'{jump.min_idx},'
            line += f'{jump.mG_lpf[jump.min_idx]},'
            line += f'{jump.mG[jump.min_idx]},'
            line += f'{jump.gyro[jump.min_idx]},'
            line += f'{jump.air_range[0]},'
            line += f'{jump.air_range[1]},'
            line += f'{jump.air_range[1] - jump.air_range[0]},'
            line += f'{jump.mG_lpf[jump.air_range[0]] if jump.air_range[0] == jump.air_range[1] else min(jump.mG_lpf[jump.air_range[0]:jump.air_range[1]])},'
            line += f'{jump.mG_lpf[jump.air_range[0]] if jump.air_range[0] == jump.air_range[1] else max(jump.mG_lpf[jump.air_range[0]:jump.air_range[1]])},'
            line += f'{jump.mG_lpf[jump.air_range[0]] if jump.air_range[0] == jump.air_range[1] else mean(jump.mG_lpf[jump.air_range[0]:jump.air_range[1]])},'
            line += f'{jump.mG_lpf[jump.air_range[0]] if jump.air_range[0] == jump.air_range[1] else std(jump.mG_lpf[jump.air_range[0]:jump.air_range[1]])},'
            line += f'{jump.mG[jump.air_range[0]] if jump.air_range[0] == jump.air_range[1] else min(jump.mG[jump.air_range[0]:jump.air_range[1]])},'
            line += f'{jump.mG[jump.air_range[0]] if jump.air_range[0] == jump.air_range[1] else max(jump.mG[jump.air_range[0]:jump.air_range[1]])},'
            line += f'{jump.mG[jump.air_range[0]] if jump.air_range[0] == jump.air_range[1] else mean(jump.mG[jump.air_range[0]:jump.air_range[1]])},'
            line += f'{jump.mG[jump.air_range[0]] if jump.air_range[0] == jump.air_range[1] else std(jump.mG[jump.air_range[0]:jump.air_range[1]])},'
            line += f'{jump.gyro[jump.air_range[0]] if jump.air_range[0] == jump.air_range[1] else min(jump.gyro[jump.air_range[0]:jump.air_range[1]])},'
            line += f'{jump.gyro[jump.air_range[0]] if jump.air_range[0] == jump.air_range[1] else max(jump.gyro[jump.air_range[0]:jump.air_range[1]])},'
            line += f'{jump.gyro[jump.air_range[0]] if jump.air_range[0] == jump.air_range[1] else mean(jump.gyro[jump.air_range[0]:jump.air_range[1]])},'
            line += f'{jump.gyro[jump.air_range[0]] if jump.air_range[0] == jump.air_range[1] else std(jump.gyro[jump.air_range[0]:jump.air_range[1]])},'
            line += f'{jump.liftoff_idx},'
            line += f'{jump.mG_lpf[jump.liftoff_idx]},'
            line += f'{jump.mG[jump.liftoff_idx]},'
            line += f'{jump.gyro[jump.liftoff_idx]},'
            line += f'{jump.touch_idx},'
            line += f'{jump.mG_lpf[jump.touch_idx]},'
            line += f'{jump.mG[jump.touch_idx]},'
            line += f'{jump.gyro[jump.touch_idx]},'
            line += f'{jump.landing_range[0]},'
            line += f'{jump.landing_range[1]},'
            line += f'{jump.landing_range[1] - jump.landing_range[0]},'
            line += f'{jump.mG_lpf[jump.landing_range[0]] if jump.landing_range[0] == jump.landing_range[1] else min(jump.mG_lpf[jump.landing_range[0]:jump.landing_range[1]])},'
            line += f'{jump.mG_lpf[jump.landing_range[0]] if jump.landing_range[0] == jump.landing_range[1] else max(jump.mG_lpf[jump.landing_range[0]:jump.landing_range[1]])},'
            line += f'{jump.mG_lpf[jump.landing_range[0]] if jump.landing_range[0] == jump.landing_range[1] else mean(jump.mG_lpf[jump.landing_range[0]:jump.landing_range[1]])},'
            line += f'{jump.mG_lpf[jump.landing_range[0]] if jump.landing_range[0] == jump.landing_range[1] else std(jump.mG_lpf[jump.landing_range[0]:jump.landing_range[1]])},'
            line += f'{jump.mG[jump.landing_range[0]] if jump.landing_range[0] == jump.landing_range[1] else min(jump.mG[jump.landing_range[0]:jump.landing_range[1]])},'
            line += f'{jump.mG[jump.landing_range[0]] if jump.landing_range[0] == jump.landing_range[1] else max(jump.mG[jump.landing_range[0]:jump.landing_range[1]])},'
            line += f'{jump.mG[jump.landing_range[0]] if jump.landing_range[0] == jump.landing_range[1] else mean(jump.mG[jump.landing_range[0]:jump.landing_range[1]])},'
            line += f'{jump.mG[jump.landing_range[0]] if jump.landing_range[0] == jump.landing_range[1] else std(jump.mG[jump.landing_range[0]:jump.landing_range[1]])},'
            line += f'{jump.gyro[jump.landing_range[0]] if jump.landing_range[0] == jump.landing_range[1] else min(jump.gyro[jump.landing_range[0]:jump.landing_range[1]])},'
            line += f'{jump.gyro[jump.landing_range[0]] if jump.landing_range[0] == jump.landing_range[1] else max(jump.gyro[jump.landing_range[0]:jump.landing_range[1]])},'
            line += f'{jump.gyro[jump.landing_range[0]] if jump.landing_range[0] == jump.landing_range[1] else mean(jump.gyro[jump.landing_range[0]:jump.landing_range[1]])},'
            line += f'{jump.gyro[jump.landing_range[0]] if jump.landing_range[0] == jump.landing_range[1] else std(jump.gyro[jump.landing_range[0]:jump.landing_range[1]])},'
            line += f'{jump.landing_range[1] - jump.air_range[0]},'
            line += f'{jump.mG_lpf[jump.air_range[0]] if jump.air_range[0] == jump.landing_range[1] else min(jump.mG_lpf[jump.air_range[0]:jump.landing_range[1]])},'
            line += f'{jump.mG_lpf[jump.air_range[0]] if jump.air_range[0] == jump.landing_range[1] else max(jump.mG_lpf[jump.air_range[0]:jump.landing_range[1]])},'
            line += f'{jump.mG_lpf[jump.air_range[0]] if jump.air_range[0] == jump.landing_range[1] else mean(jump.mG_lpf[jump.air_range[0]:jump.landing_range[1]])},'
            line += f'{jump.mG_lpf[jump.air_range[0]] if jump.air_range[0] == jump.landing_range[1] else std(jump.mG_lpf[jump.air_range[0]:jump.landing_range[1]])},'
            line += f'{jump.mG[jump.air_range[0]] if jump.air_range[0] == jump.landing_range[1] else min(jump.mG[jump.air_range[0]:jump.landing_range[1]])},'
            line += f'{jump.mG[jump.air_range[0]] if jump.air_range[0] == jump.landing_range[1] else max(jump.mG[jump.air_range[0]:jump.landing_range[1]])},'
            line += f'{jump.mG[jump.air_range[0]] if jump.air_range[0] == jump.landing_range[1] else mean(jump.mG[jump.air_range[0]:jump.landing_range[1]])},'
            line += f'{jump.mG[jump.air_range[0]] if jump.air_range[0] == jump.landing_range[1] else std(jump.mG[jump.air_range[0]:jump.landing_range[1]])},'
            line += f'{jump.gyro[jump.air_range[0]] if jump.air_range[0] == jump.landing_range[1] else min(jump.gyro[jump.air_range[0]:jump.landing_range[1]])},'
            line += f'{jump.gyro[jump.air_range[0]] if jump.air_range[0] == jump.landing_range[1] else max(jump.gyro[jump.air_range[0]:jump.landing_range[1]])},'
            line += f'{jump.gyro[jump.air_range[0]] if jump.air_range[0] == jump.landing_range[1] else mean(jump.gyro[jump.air_range[0]:jump.landing_range[1]])},'
            line += f'{jump.gyro[jump.air_range[0]] if jump.air_range[0] == jump.landing_range[1] else std(jump.gyro[jump.air_range[0]:jump.landing_range[1]])},'
            line += f'{jump.impulse_idx},'
            line += f'{jump.mG_lpf[jump.impulse_idx]},'
            line += f'{jump.mG[jump.impulse_idx]},'
            line += f'{jump.gyro[jump.impulse_idx]},'
            line += f'{jump.distance},'
            line += f'{jump.tests_passed},'
            line += f'{jump.total_tests},'
            line += f'{jump.confidence},'
            line += f'{len(jump.mG_lpf)},'
            line += f'{min(jump.mG_lpf)},'
            line += f'{max(jump.mG_lpf)},'
            line += f'{mean(jump.mG_lpf)},'
            line += f'{std(jump.mG_lpf)},'
            line += f'{min(jump.mG)},'
            line += f'{max(jump.mG)},'
            line += f'{mean(jump.mG)},'
            line += f'{std(jump.mG)},'
            line += f'{min(jump.gyro)},'
            line += f'{max(jump.gyro)},'
            line += f'{mean(jump.gyro)},'
            line += f'{std(jump.gyro)}'
            line += '\n'
            self.file_train.write(line)


    def identifyJumps(self, override_th=None):
        """Identify all points of low G-force and run the jump id pipeline on each.
        
        Confidence values will be associated with each `Jump` instance.
        """
        lowG_els = identifyRangesBelowTH(
            self.mG_lpf(),
            Jump.mGThreshold() if override_th is None else override_th
        )
        self.jumps = [Jump(el, self.mG_lpf(), self.mG, self.gyro) for el in lowG_els]
        self.logJumpData(override_th)

    
    def identifyTurns(self): pass

