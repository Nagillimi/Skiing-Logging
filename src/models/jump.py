import numpy as np
from constants.jump_th import JUMP_THRESHOLD_MG
from domain.evaluated_kinematics import EvaluatedKinematics
from domain.g_force import GForce
from domain.session_logger import SessionLogger as logger
from utilities.sig_proc_np import maxIndex, minIndex
from utilities.sig_proc import cumtrapz
from utilities.stat_tests import StatTests as ST

class Jump(EvaluatedKinematics):
    def __init__(
            self,
            lowG_range: np.ndarray,
            g_force: GForce,
            gyro: np.ndarray,
    ) -> None:
        super().__init__()

        self.lowG_range = lowG_range
        self.mG_lpf = g_force.mG_lpf
        self.mG = g_force.mG
        self.gyro = gyro

        self.identify()


    @property
    def air_time(self):
        """Calculate the air time from `liftoff_idx` and the beginning of the landing, `touch_idx`"""
        # indices are in 100Hz
        return (self.touch_idx - self.liftoff_idx) / 100

    @property
    def distance(self):
        """Calculate the jump distance based on the integration of the Tile
        acceleration subtracting gravity.

        Note, this assumes that the only other acceleration next to gravity is pure motion.
        Friction and drag are neglected.
        """
        # integrate (mG_lpf - 1G) to get velocity
        vel = cumtrapz(self.mG_lpf - 1)
        mean_air_time_vel = np.mean(vel[self.liftoff_idx:self.touch_idx])
        return mean_air_time_vel * self.air_time


    def computeMinIndex(self):
        self.lowest_mG_lpf = self.mG_lpf[self.lowG_range[0]]
        self.lowest_mG = self.mG[self.lowG_range[0]]
        if self.lowG_range[0] != self.lowG_range[1]:
            self.lowest_mG_lpf = min(self.mG_lpf[self.lowG_range[0]:self.lowG_range[1]])
            self.lowest_mG = min(self.mG[self.lowG_range[0]:self.lowG_range[1]])

        self.min_idx = minIndex(self.mG_lpf, self.lowG_range)
        logger.debug(f'min_idx:\t\t{self.min_idx}')


    def computeAirPhase(self, th=2, method='std'):
        """Calculate the index range of total air time, where `min_idx` is the last element.
        Scans the left of `mG_lpf` signal for start of the decline to the min_idx of low G.

        Store the maximum seen before `min_idx` in `mG_lpf` as the `liftoff_idx`.
        """
        if method == 'std':
            # std-based method, search left and right until the window std dev passes a th
            N = self.mG.shape[0]
            wsamples = 16
            self.liftoff_idx = self.min_idx
            self.touch_idx = self.min_idx
            for i in range(self.min_idx + 1 - wsamples):
                # build sliding window & test std
                if np.std(self.mG[self.min_idx - (wsamples + i):self.min_idx - i]) > 400:
                    self.liftoff_idx = self.min_idx - (i + round(wsamples / 2))
                    break

            for i in range(N - self.min_idx + 1 - wsamples):
                if np.std(self.mG[self.min_idx + i:self.min_idx + (wsamples + i)]) > 1000:
                    self.touch_idx = self.min_idx + (i + round(wsamples / 2))
                    break

        else:
            x1 = 0
            for i in range(len(self.mG_lpf[0:self.min_idx])):
                if self.mG_lpf[self.min_idx - i] - self.mG_lpf[self.min_idx - (i + 1)] > th:
                    x1 = self.min_idx - (i + 1)
                    break
            self.liftoff_idx = maxIndex(self.mG_lpf, [x1, self.min_idx])

            # now search right of `min_idx` to find the point where G's increase, signifying landing
            for i in range(len(self.mG_lpf[self.min_idx:-1])):
                if self.mG_lpf[self.min_idx + i] > JUMP_THRESHOLD_MG:
                    self.touch_idx = self.min_idx + i
                    break

        self.air_range =  [self.liftoff_idx, self.touch_idx]
        logger.debug(f'air_range:\t{self.air_range}')


    def computeLandingPhase(self, delay_s=0.5):
        """Calculate the index range of the landing phase, where `min_idx` is the first element.
        Uses a static delay of `delay_s` after a small increase is observed in the `mG_lpf`.

        Store the impulse seen in `mG` as the `impulse_idx`.
        """
        self.landing_range = [self.touch_idx, int(self.touch_idx + delay_s * 100)]
        self.impulse_idx = maxIndex(self.mG, self.landing_range)
        logger.debug(f'landing_range:\t{self.landing_range}')
    

    def testSuite(self) -> np.ndarray:
        """Run the test suite. Can toggle individual running here.
        
        In the future, can return values and parameters for each test. For ML
        """
        logger.debug('Running test suite.')
        return np.array([
            ST.testDecreasingTrend(self.mG_lpf, self.air_range, header='Test mG_lpf has decreasing trend during air range'),
            ST.testMinSampleCount(self.air_range, min_count=30, header='Test air_range has minimum 30 sample count'),
            ST.testMinSampleCount(self.lowG_range, min_count=10, header='Test lowG_range has minimum 10 samples below lowG threshold'),
            ST.testLowerSampleStdDev(self.mG, self.air_range, header='Test mG std dev (air time < pop)'),
            ST.testLowerSampleStdDev(self.gyro, self.air_range, header='Test gyro std dev (air time < pop)'),
            ST.testLowerSampleMean(self.mG, self.air_range, header='Test mG mean (air time < pop)'),
            # ST.testLowerSampleMean(self.gyro, self.air_range, header='Test gyro mean (air time < pop)'),
            ST.testLowerSampleStdDev(self.mG, self.air_range, self.landing_range, header='Test mG std dev (air time < landing time)'),
            ST.testLowerSampleStdDev(self.gyro, self.air_range, self.landing_range, header='Test gyro std dev (air time < landing time)'),
            ST.testLowerSampleMean(self.mG, self.air_range, self.landing_range, header='Test mG mean (air time < landing time)'),
            # ST.testLowerSampleMean(self.gyro, self.air_range, self.landing_range, header='Test gyro mean (air time < landing time)'),
            ST.testLargerSampleStdDev(self.mG, self.landing_range, header='Test mG std dev (landing time > pop)'),
            ST.testLargerSampleStdDev(self.gyro, self.landing_range, header='Test gyro std dev (landing time > pop)'),
            ST.testLargerSampleMean(self.mG, self.landing_range, header='Test mG mean (landing time > pop)'),
            ST.testLargerSampleMean(self.gyro, self.landing_range, header='Test gyro mean (landing time > pop)'),
            ST.testLargestMagnitude(self.mG, self.air_range, header='Test landing time mG contains large impulse > (3 * std dev)'),
            ST.testTimingOfMagnitude(self.mG, self.landing_range, header='Test that large impulse occurs close to landing time'),
        ])
    
    
    def identify(self):
        """Identifies the ranges of air time and landing"""
        logger.debug('New jump identification.')
        self.computeMinIndex()
        self.computeAirPhase()
        self.computeLandingPhase()
        self.test(self.testSuite)
    
