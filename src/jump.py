from sig_proc_np import maxIndex, minIndex
from sig_proc import cumtrapz
from stat_tests import StatTests as ST
import numpy as np

JUMP_THRESHOLD_MG = 600
"""The static low mG threshold to trigger jump identification."""

class Jump:
    def __init__(self,
            lowG_range: np.ndarray,
            mG_lpf: np.ndarray,
            mG: np.ndarray,
            gyro: np.ndarray,
            print_out=False
    ) -> None:
        self.lowG_range = lowG_range
        self.mG_lpf = mG_lpf
        self.mG = mG
        self.gyro = gyro
        self.confidence = 0.
        self.tests_passed = 0
        self.total_tests = 0

        self.identify(print_out=print_out)


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


    def computeMinIndex(self, print_out=False):
        self.lowest_mG_lpf = self.mG_lpf[self.lowG_range[0]]
        self.lowest_mG = self.mG[self.lowG_range[0]]
        if self.lowG_range[0] != self.lowG_range[1]:
            self.lowest_mG_lpf = min(self.mG_lpf[self.lowG_range[0]:self.lowG_range[1]])
            self.lowest_mG = min(self.mG[self.lowG_range[0]:self.lowG_range[1]])

        self.min_idx = minIndex(self.mG_lpf, self.lowG_range)
        if print_out: print('min_idx:\t\t', self.min_idx)


    def computeAirPhase(self, th=2, print_out=False, method='std'):
        """Calculate the index range of total air time, where `min_idx` is the last element.
        Scans the left of `mG_lpf` signal for start of the decline to the min_idx of low G.

        Store the maximum seen before `min_idx` in `mG_lpf` as the `liftoff_idx`.
        """
        if method == 'std':
            # std-based method, search left and right until the window std dev passes a th
            wsamples = 16
            self.liftoff_idx = self.min_idx
            self.touch_idx = self.min_idx
            for i in range(len(self.mG[0:self.min_idx]) - wsamples):
                # build sliding window & test std
                if np.std(self.mG[self.min_idx - (wsamples + i):self.min_idx - i]) > 400:
                    self.liftoff_idx = self.min_idx - (i + round(wsamples / 2))
                    break

            for i in range(len(self.mG[self.min_idx:-1]) - wsamples):
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
        if print_out: print('air_range:\t', self.air_range)


    def computeLandingPhase(self, delay_s=0.5, print_out=False):
        """Calculate the index range of the landing phase, where `min_idx` is the first element.
        Uses a static delay of `delay_s` after a small increase is observed in the `mG_lpf`.

        Store the impulse seen in `mG` as the `impulse_idx`.
        """
        self.landing_range = [self.touch_idx, int(self.touch_idx + delay_s * 100)]
        self.impulse_idx = maxIndex(self.mG, self.landing_range)
        if print_out: print('landing_range:\t', self.landing_range)
    

    def runTestSuite(self, print_out=False) -> np.ndarray:
        """Run the test suite. Can toggle individual running here.
        
        In the future, can return values and parameters for each test. For ML
        """
        return np.array([
            ST.testDecreasingTrend(self.mG_lpf, self.air_range, print_out=print_out, header='Test mG_lpf has decreasing trend'),
            ST.testMinSampleCount(self.mG_lpf, self.air_range, print_out=print_out, header='Test mG_lpf has minimum sample count'),
            ST.testMinSampleCount(self.mG_lpf, self.lowG_range, min_count=10, print_out=print_out, header='Test mG_lpf has minimum samples below lowG threshold'),
            ST.testLowerSampleStdDev(self.mG, self.air_range, print_out=print_out, header='Test mG std dev (air time < pop)'),
            ST.testLowerSampleStdDev(self.gyro, self.air_range, print_out=print_out, header='Test gyro std dev (air time < pop)'),
            ST.testLowerSampleMean(self.mG, self.air_range, print_out=print_out, header='Test mG mean (air time < pop)'),
            # ST.testLowerSampleMean(self.gyro, self.air_range, print_out=print_out, header='Test gyro mean (air time < pop)'),
            ST.testLowerSampleStdDev(self.mG, self.air_range, self.landing_range, print_out=print_out, header='Test mG std dev (air time < landing time)'),
            ST.testLowerSampleStdDev(self.gyro, self.air_range, self.landing_range, print_out=print_out, header='Test gyro std dev (air time < landing time)'),
            ST.testLowerSampleMean(self.mG, self.air_range, self.landing_range, print_out=print_out, header='Test mG mean (air time < landing time)'),
            # ST.testLowerSampleMean(self.gyro, self.air_range, self.landing_range, print_out=print_out, header='Test gyro mean (air time < landing time)'),
            ST.testLargerSampleStdDev(self.mG, self.landing_range, print_out=print_out, header='Test mG std dev (landing time > pop)'),
            ST.testLargerSampleStdDev(self.gyro, self.landing_range, print_out=print_out, header='Test gyro std dev (landing time > pop)'),
            ST.testLargerSampleMean(self.mG, self.landing_range, print_out=print_out, header='Test mG mean (landing time > pop)'),
            ST.testLargerSampleMean(self.gyro, self.landing_range, print_out=print_out, header='Test gyro mean (landing time > pop)'),
            ST.testLargeImpulse(self.mG, self.air_range, print_out=print_out, header='Test landing time mG contains large impulse > (3 * std dev)'),
            ST.testTimingOfLargeImpulse(self.mG, self.landing_range, print_out=print_out, header='Test that large impulse occurs close to landing time'),
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
        """Identifies the ranges of air time and landing"""
        self.computeMinIndex(print_out=print_out)
        self.computeAirPhase(print_out=print_out)
        self.computeLandingPhase(print_out=print_out)
        self.test(print_out=print_out)
    
