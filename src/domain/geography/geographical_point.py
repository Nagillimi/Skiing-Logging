

class GeographicalPoint:
    """Geometric point that represents a moment in time and space."""
    def __init__(
            self,
            pt_type: str,
            ts: float,
            idx: int,
            alt: float = None,
    ) -> None:
        self.pt_type = pt_type
        self.ts = ts
        self.idx = idx
        self.alt = alt


    @property
    def pt_type(self) -> str:
        """Geographical point type, either `lb`, `lp`, `rp`, `rb`."""
        return self.__pt_type
    
    @pt_type.setter
    def pt_type(self, pt_type):
        self.__pt_type = pt_type

    @property
    def ts(self) -> float:
        return self.__ts
    
    @ts.setter
    def ts(self, ts):
        self.__ts = ts


    @property
    def idx(self) -> int:
        return self.__idx
    
    @idx.setter
    def idx(self, idx):
        self.__idx = idx


    @property
    def alt(self) -> float:
        return self.__alt
    
    @alt.setter
    def alt(self, alt):
        self.__alt = alt
