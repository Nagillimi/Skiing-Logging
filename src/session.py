from io import TextIOWrapper
from datafile import constructJumpLine, createJumpDataFile
from decode import decodeA50, decodeF6P, decodeTile
from jump import JUMP_THRESHOLD_MG
from tile import Tile

class Session:
    def __init__(
            self,
            tile_file,
            a50_file,
            f6p_file,
            offsets=None,
            print_out=False,
            compute_kinematics=True,
    ) -> None:
        # init the device objects
        self.raw_tile = decodeTile(tile_file, print_out, "Raw Tile")
        self.a50 = decodeA50(a50_file, print_out, "A50")
        self.f6p = decodeF6P(f6p_file, print_out, "F6P")

        self.tile = Tile(self.raw_tile)
        if offsets is None:
            self.tile.identifyOffsets(self.a50)
        else:
            self.tile.applyOffsets(offsets[0], offsets[1])
            self.tile.applyTimestamp(self.a50[0].time[0])

        if not compute_kinematics:
            return 
        
        # these will be called internal to Tile, but for now
        # self.tile.computeJumps()
        self.tile.computeStaticRegistrations()
        self.tile.computeTurns()

        # build logging files
        # self.logJumpData()


    def logJumpData(self):
        self.jump_train_file = createJumpDataFile(f'tile-{self.a50[0].date}-jumps-{JUMP_THRESHOLD_MG}mG.csv')
        self.jump_train_file.writelines([constructJumpLine(jump) for jump in self.tile.jumps])
        self.jump_train_file.close()


    @property
    def jump_train_file(self) -> TextIOWrapper:
        return self.__jump_train_file

    @jump_train_file.setter
    def jump_train_file(self, f):
        self.__jump_train_file = f

