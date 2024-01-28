from decode import decodeA50, decodeF6P, decodeTile
from tile import Tile

class Session:
    def __init__(
            self,
            tile_file,
            a50_file,
            f6p_file,
            offsets=None,
            print_out=False,
    ) -> None:
        self.raw_tile = decodeTile(tile_file, print_out, "Raw Tile")
        self.a50 = decodeA50(a50_file, print_out, "A50")
        self.f6p = decodeF6P(f6p_file, print_out, "F6P")

        self.tile = Tile(self.raw_tile)
        if offsets is None:
            self.tile.identifyOffsets(self.a50)
        else:
            self.tile.applyOffsets(offsets)
            self.tile.applyTimestamp(self.a50[0].time[0])
        self.tile.computeJumps()
        self.tile.computeStaticRegistrations()
        self.tile.computeTurns()


    @property
    def jump_train_file(self):
        return self.__jump_train_file


    @jump_train_file.setter
    def jump_train_file(self, f):
        self.__jump_train_file = f

