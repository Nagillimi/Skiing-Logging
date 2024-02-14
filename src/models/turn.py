import numpy as np
from domain.g_force import GForce
from utilities.quat import quatToEuler
from utilities.sig_proc_np import maxIndex, zeroCrossingIdxs
from utilities.stat_tests import StatTests as ST

class Turn:
    def __init__(self,
            highG_idx: int,
            g_force: GForce,
            boot_quat: np.ndarray,
            print_out=False
    ) -> None:
        self.highG_idx = highG_idx
        self.g_force = g_force
        self.boot_euler = np.apply_along_axis(quatToEuler, 1, boot_quat)
        self.confidence = 0.
        self.tests_passed = 0
        self.total_tests = 0

        self.identify(print_out=print_out)


    def identifyIdxs(self):
        """Identifies various indices that represent important turning kinematics.
        
        - turn baseline idx based on the most recent derivative zero crossing with a positive slope.
        - max roll idx between baseline roll and high G indices
        """
        self.baseline_idx = np.max(zeroCrossingIdxs(self.g_force.d_mG_lpf_dt[:self.highG_idx - 1]))
        self.min_dF_dt_idx = np.max(zeroCrossingIdxs(self.g_force.d2_mG_lpf_dt2[:self.baseline_idx - 1]))

        baseline_roll = self.boot_euler[self.baseline_idx, 0]
        offset_roll = self.boot_euler[self.baseline_idx:self.highG_idx, 0] + baseline_roll
        self.max_roll_idx = self.baseline_idx + maxIndex(np.abs(offset_roll))

        # baseline_flex = self.boot_euler[self.baseline_idx, 1]


    def identifySide(self):
        """Identifies the turning side (uphill/downhill) based on the sign of the roll
        """
        self.side = 'D' if self.boot_euler[self.baseline_idx, 0] < self.boot_euler[self.max_roll_idx, 0] else 'U'


    def computeCarvingAngle(self):
        """Using the baseline.
        """
        self.carving_angle = abs(self.boot_euler[self.baseline_idx, 0] - self.boot_euler[self.max_roll_idx, 0])


    def runTestSuite(self, print_out=False) -> np.ndarray:
        """Run the test suite. Can toggle individual running here.
        
        In the future, can return values and parameters for each test. For ML
        """
        return np.array([
            True
        ])
    

    def test(self, print_out=False):
        """Runs the internal test suite to determine the confidence value of the jump identification.
        Currently, all tests are weighted equally.
        
        Returns the number of tests passed, total tests, and the confidence value in %.
        """
        results = self.runTestSuite(print_out=print_out)
        self.tests_passed = np.sum(results)
        self.total_tests = results.shape[0]
        self.confidence = self.tests_passed / self.total_tests * 100
    
    
    def identify(self, print_out=False):
        """"""
        # compute any key elements of the turn
        self.identifyIdxs()
        self.identifySide()
        self.computeCarvingAngle()
        # self.computeFlex()
        self.test(print_out=print_out)


    @property
    def highG_idx(self) -> int:
        """Index of high G at max compression in turn."""
        return self.__highG_idx

    @highG_idx.setter
    def highG_idx(self, highG_idx):
        self.__highG_idx = highG_idx

    @property
    def baseline_idx(self) -> int:
        """Index of baseline before turn start."""
        return self.__baseline_idx

    @baseline_idx.setter
    def baseline_idx(self, baseline_idx):
        self.__baseline_idx = baseline_idx


    @property
    def max_roll_idx(self) -> int:
        """Index of max_roll before turn start."""
        return self.__max_roll_idx

    @max_roll_idx.setter
    def max_roll_idx(self, max_roll_idx):
        self.__max_roll_idx = max_roll_idx


    @property
    def side(self) -> str:
        """Side of turn, uphill or downhill (`U`, `D`)."""
        return self.__side

    @side.setter
    def side(self, side):
        self.__side = side