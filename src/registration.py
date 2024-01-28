import numpy as np

class Registration:
    def __init__(
            self,
            ts: float,
            reg_quat: np.ndarray
    ) -> None:
        self.timestamp = ts
        self.reg_quat = reg_quat