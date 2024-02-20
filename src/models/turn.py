import numpy as np
from constants.ski_th import SKI_SIDECUT_R
from domain.evaluated_kinematics import EvaluatedKinematics
from domain.g_force import GForce
from domain.session_logger import SessionLogger as logger
from utilities.quat import quatToEuler
from utilities.sig_proc_np import deriv, zeroCrossingIdxs
from utilities.stat_tests import StatTests as ST

class Turn(EvaluatedKinematics):
    def __init__(
            self,
            highG_idx: int,
            alt_lpf: np.ndarray,
            g_force: GForce,
            boot_euler: np.ndarray,
            d_boot_euler_dt: np.ndarray,
    ) -> None:
        super().__init__()
        
        self.highG_idx = highG_idx
        self.g_force = g_force
        self.alt_lpf = alt_lpf
        self.roll = boot_euler[:, 0]
        self.d_boot_roll_dt = d_boot_euler_dt[:, 0]

        self.identify()


    def identifyIdxs(self):
        """Identifies various indices that represent important turning kinematics.
        
        - turn baseline idx based on the most recent derivative zero crossing with a positive slope.
        - max roll idx between baseline roll and high G indices
        """
        logger.debug('Identifying key indices in accleration and boot roll.')

        self.baseline_idx_1 = np.max(zeroCrossingIdxs(self.g_force.d_mG_lpf_dt[:self.highG_idx - 1]))
        self.baseline_idx_2 = np.max(zeroCrossingIdxs(self.g_force.d2_mG_lpf_dt2[:self.baseline_idx_1 - 1]))
        self.baseline_idx_3 = round((self.baseline_idx_1 + self.baseline_idx_2) * 0.5)

        self.peak_roll_idx = np.max(zeroCrossingIdxs(self.d_boot_roll_dt[:self.highG_idx - 1]))
        self.past_peak_roll_idx = np.max(zeroCrossingIdxs(self.d_boot_roll_dt[:self.peak_roll_idx - 1]))

        self.baseline_idx_4 = round((self.peak_roll_idx + self.past_peak_roll_idx) * 0.5)

        mean_roll = np.mean(self.roll[self.past_peak_roll_idx:self.peak_roll_idx])
        
        # if a right turn (past pk < pk)
        if self.roll[self.past_peak_roll_idx] < self.roll[self.peak_roll_idx]:
            idxs_above_mean = np.argwhere(
                self.roll[self.past_peak_roll_idx:self.peak_roll_idx] > mean_roll
            )
        # else a left turn (past pk > pk)
        else:
            idxs_above_mean = np.argwhere(
                self.roll[self.past_peak_roll_idx:self.peak_roll_idx] < mean_roll
            )

        self.baseline_idx_5 = self.past_peak_roll_idx + np.min(idxs_above_mean)

        # baseline_flex = self.boot_euler[self.baseline_idx, 1]

        self.turn_range = [self.baseline_idx_1, self.highG_idx]
        self.baseline_range = [self.baseline_idx_2, self.baseline_idx_1]
        self.min_radius_range = [self.peak_roll_idx, self.highG_idx]
        self.offset_abs_roll = np.absolute(self.roll[self.baseline_idx_1:self.highG_idx] + self.roll[self.baseline_idx_1])
        # self.heading_change = abs(self.boot_euler[self.highG_idx, 2] - self.boot_euler[self.baseline_idx_1, 2])


    def identifySide(self):
        """Identifies the turning side (uphill/downhill) based on the sign of the roll
        """
        self.side = 'D' if self.roll[self.baseline_idx_1] < self.roll[self.peak_roll_idx] else 'U'


    def computeCarvingAngle(self):
        """Using the baseline angle, compute the carving angle in the boot frame."""
        logger.debug('Computing the carving angle based on the identified indices.')

        def maxCarveFromBaseline(baseline_idx):
            return abs(self.roll[baseline_idx] - self.roll[self.peak_roll_idx])
        
        self.carving_angle_1 = maxCarveFromBaseline(self.baseline_idx_1)
        self.carving_angle_2 = maxCarveFromBaseline(self.baseline_idx_2)
        self.carving_angle_3 = maxCarveFromBaseline(self.baseline_idx_3)
        self.carving_angle_4 = maxCarveFromBaseline(self.baseline_idx_4)
        self.carving_angle_5 = maxCarveFromBaseline(self.baseline_idx_5)

        self.turning_radius = SKI_SIDECUT_R * np.cos(np.deg2rad(self.offset_abs_roll))


    def testSuite(self) -> np.ndarray:
        """Run the test suite. Can toggle individual running here.
        
        In the future, can return values and parameters for each test. For ML
        """
        logger.debug('Running test suite.')
        return np.array([
            ST.testDecreasingTrend(self.alt_lpf, self.turn_range, header='Test alt_lpf has decreasing trend'),
            ST.testMinSampleCount(self.turn_range, min_count=35, header='Test for minimum samples count'),
            ST.testRecentMax(self.offset_abs_roll, th=25, header='Test that the max carving occurs close to the max compression'),
            ST.testLargestMagnitude(self.offset_abs_roll, th=20, header='Test carve angle > 30deg'),
            ST.testLargestMagnitude(self.g_force.mG_lpf, self.turn_range, th=1250, header='Test max g-force > 1250mG'),
            ST.testLowerSampleStdDev(
                self.offset_abs_roll,
                [self.peak_roll_idx - self.baseline_idx_1, len(self.min_radius_range) - 1],
                [0, len(self.baseline_range) - 1],
                header='Test roll std dev (min radius < baseline)'
            ),
            ST.testSmallestMagnitude(self.g_force.mG_lpf, self.turn_range, th=1000, header='Test g-force at baseline < 1000mG'),
        ])
    
    
    def identify(self):
        """Identifies the complete turning kinematics and runs the test suite, assigning a confidence value
        based on specific statistical tests.
        """
        logger.debug('New turn identification.')
        self.identifyIdxs()
        self.identifySide()
        self.computeCarvingAngle()
        self.test(self.testSuite)


    @property
    def highG_idx(self) -> int:
        """Index of high G at max compression in turn."""
        return self.__highG_idx

    @highG_idx.setter
    def highG_idx(self, highG_idx):
        self.__highG_idx = highG_idx


    @property
    def baseline_idx_1(self) -> int:
        """Index of baseline before turn start."""
        return self.__baseline_idx

    @baseline_idx_1.setter
    def baseline_idx_1(self, baseline_idx):
        self.__baseline_idx = baseline_idx


    @property
    def peak_roll_idx(self) -> int:
        """Index of max_roll before turn start."""
        return self.__peak_roll_idx

    @peak_roll_idx.setter
    def peak_roll_idx(self, peak_roll_idx):
        self.__peak_roll_idx = peak_roll_idx


    @property
    def side(self) -> str:
        """Side of turn, uphill or downhill (`U`, `D`)."""
        return self.__side

    @side.setter
    def side(self, side):
        self.__side = side