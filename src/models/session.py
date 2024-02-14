from io import TextIOWrapper
from domain.decode.decode_a50 import decodeA50
from domain.decode.decode_f6p import decodeF6P
from domain.decode.decode_tile import decodeTile
from domain.jump import JUMP_THRESHOLD_MG
from domain.tile import Tile
from utilities.datafile import constructJumpLine, constructSensorBootLines, createJumpDataFile, createSensorBootDataFile

class Session:
    def __init__(
            self,
            tile_file,
            a50_file=None,
            f6p_file=None,
            offsets=None,
            print_out=False,
            compute_kinematics=True,
    ) -> None:
        # init the device objects
        self.raw_tile = decodeTile(tile_file, print_out, "Raw Tile")
        self.tile = Tile(
            self.raw_tile,
            print_out=print_out,
            compute_kinematics=compute_kinematics
        )

        if a50_file is not None:
            self.a50 = decodeA50(a50_file, print_out, "A50")
            if offsets is None:
                self.tile.identifyOffsets(self.a50, print_out=print_out)
            else:
                self.tile.applyOffsets(offsets[0], offsets[1])
                self.tile.applyTimestamp(self.a50[0].time[0])

        if f6p_file is not None:
            self.f6p = decodeF6P(f6p_file, print_out, "F6P")

        self.logJumpData()
        self.logSensorBootData()


    def logJumpData(self):
        self.jump_train_file = createJumpDataFile(f'tile-{self.a50[0].date}-jumps-{JUMP_THRESHOLD_MG}mG.csv')
        self.jump_train_file.writelines([constructJumpLine(jump) for jump in self.tile.jumps])
        self.jump_train_file.close()


    def logSensorBootData(self):
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

