from io import TextIOWrapper
from constants.jump_th import JUMP_THRESHOLD_MG
from constants.turn_th import D_MG_LPF_DT_TH
from domain.decode.decode_a50 import decodeA50
from domain.decode.decode_f6p import decodeF6P
from domain.decode.decode_tile import decodeTile
from domain.session_logger import SessionLogger as logger
from models.tile import Tile
from utilities.datafile import (
    constructJumpLine,
    constructSensorBootLines,
    constructTurnLine,
    createJumpDataFile,
    createSensorBootDataFile,
    createTurnDataFile
)

class Session:
    def __init__(
            self,
            tile_file,
            a50_file=None,
            f6p_file=None,
            offsets=None,
            compute_kinematics=True,
            import_non_tile=True,
    ) -> None:
        # init the device objects
        self.raw_tile = decodeTile(tile_file)
        self.tile = Tile(raw=self.raw_tile, compute_kinematics=compute_kinematics)

        if a50_file is not None and import_non_tile is True:
            self.a50 = decodeA50(a50_file)
            if offsets is None:
                self.tile.identifyOffsets(self.a50)
            else:
                self.tile.applyOffsets(offsets[0], offsets[1])
                self.tile.applyTimestamp(self.a50[0].time[0])

        if f6p_file is not None and import_non_tile is True:
            self.f6p = decodeF6P(f6p_file)

        self.logJumpData()
        self.logTurnData()
        # self.logSensorBootOrientationData()

        logger.info('Done importing session.\n')


    def logJumpData(self):
        logger.info('Generating jump training file.')
        self.jump_train_file = createJumpDataFile(f'tile-{self.a50[0].date}-jumps-{JUMP_THRESHOLD_MG}mG.csv')
        self.jump_train_file.writelines([constructJumpLine(jump) for jump in self.tile.jumps])
        self.jump_train_file.close()


    def logTurnData(self):
        logger.info('Generating turn training file.')
        self.turn_train_file = createTurnDataFile(f'tile-{self.a50[0].date}-turns-{D_MG_LPF_DT_TH}d_mG_lpf_dt.csv')
        self.turn_train_file.writelines([constructTurnLine(turn) for turn in self.tile.turns])
        self.turn_train_file.close()


    def logSensorBootOrientationData(self):
        self.euler_sensor_boot_file = createSensorBootDataFile(f'tile-{self.a50[0].date}-sensor-boot-frame.csv')
        self.euler_sensor_boot_file.write(constructSensorBootLines(self.tile))
        self.euler_sensor_boot_file.close()
    

    @property
    def jump_train_file(self) -> TextIOWrapper:
        return self.__jump_train_file

    @jump_train_file.setter
    def jump_train_file(self, f):
        self.__jump_train_file = f


    @property
    def euler_sensor_boot_file(self) -> TextIOWrapper:
        return self.__euler_sensor_boot_file

    @euler_sensor_boot_file.setter
    def euler_sensor_boot_file(self, f):
        self.__euler_sensor_boot_file = f

