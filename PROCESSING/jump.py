from jump_tests import JumpTests
from signal_processing import maxIndex, mean, minIndex, trapz

class Jump(JumpTests):
    def __init__(self, lowG_range: [], mG_lpf: [], mG: [], gyro: [], print_out=False) -> None:
        self.lowG_range = lowG_range
        self.mG_lpf = mG_lpf
        self.mG = mG
        self.gyro = gyro
        self.confidence = 0.
        self.tests_passed = 0
        self.total_tests = 0
        self.identify(print_out=print_out)


    @staticmethod
    def mGThreshold():
        """The static low mG threshold to trigger jump identification."""
        return 600


    @property
    def airTime(self):
        """Calculate the air time from `liftoff_idx` and the landing impulse, `landing_idx`"""
        # indices are in 100Hz
        return (self.landing_idx - self.liftoff_idx) / 100


    @property
    def distance(self):
        """Calculate the jump distance based on the integration of the Tile
        acceleration subtracting gravity
        """
        # integrate (1G - mG_lpf) to get velocity
        vel = trapz([a - 1 for a in self.mG_lpf])
        mean_air_time_vel = mean(vel[self.liftoff_idx:self.landing_idx])
        # TODO should I use v2-v1 here

        return mean_air_time_vel * self.airTime


    def computeAirPhase(self, th=2, print_out=False):
        """Calculate the index range of total air time, where `min_idx` is the last element.
        Scans the left of `mG_lpf` signal for start of the decline to the min_idx of low G.

        Store the maximum seen before `min_idx` in `mG_lpf` as the `liftoff_idx`.
        """
        x1 = 0
        for i in range(len(self.mG_lpf[0:self.min_idx])):
            if self.mG_lpf[self.min_idx - i] - self.mG_lpf[self.min_idx - (i + 1)] > th:
                x1 = self.min_idx - (i + 1)
                break
        self.liftoff_idx = maxIndex(self.mG_lpf, [x1, self.min_idx])
        self.air_range =  [self.liftoff_idx, self.min_idx]
        if print_out: print('air_range:\t', self.air_range)
    

    def computeLandingPhase(self, delay_s=0.5, print_out=False):
        """Calculate the index range of the landing phase, where `min_idx` is the first element.
        Uses a static delay of `delay_s` after a small increase is observed in the `mG_lpf`.

        Store the impulse seen in `mG` as the `landing_idx`.
        """
        touch_idx = 0
        for i in range(len(self.mG_lpf[self.min_idx:-1])):
            if self.mG_lpf[self.min_idx + (i + 1)] - self.mG_lpf[self.min_idx + i] > 10:
                touch_idx = self.min_idx + i + 1
                break

        x2 = int(touch_idx + delay_s * 100)
        self.landing_range = [self.min_idx, x2]
        self.landing_idx = maxIndex(self.mG, self.landing_range)
        if print_out: print('landing_range:\t', self.landing_range)
    

    def runTestSuite(self, print_out=False):
        """Run the test suite. Can toggle individual running here."""
        return [
            self.testForDecreasingTrend(self.mG_lpf, self.air_range, print_out=print_out, header='Test mG_lpf has decreasing trend'),
            self.testForMinSampleCount(self.mG_lpf, self.air_range, print_out=print_out, header='Test mG_lpf has minimum sample count'),
            self.testForLowerSampleStdDev(self.mG, self.air_range, print_out=print_out, header='Test mG std dev (air time < pop)'),
            self.testForLowerSampleStdDev(self.gyro, self.air_range, print_out=print_out, header='Test gyro std dev (air time < pop)'),
            self.testForLowerSampleMean(self.mG, self.air_range, print_out=print_out, header='Test mG mean (air time < pop)'),
            # self.testForLowerSampleMean(self.gyro, self.air_range, print_out=print_out, header='Test gyro mean (air time < pop)'),
            self.testForLowerSampleStdDev(self.mG, self.air_range, self.landing_range, print_out=print_out, header='Test mG std dev (air time < landing time)'),
            self.testForLowerSampleStdDev(self.gyro, self.air_range, self.landing_range, print_out=print_out, header='Test gyro std dev (air time < landing time)'),
            self.testForLowerSampleMean(self.mG, self.air_range, self.landing_range, print_out=print_out, header='Test mG mean (air time < landing time)'),
            # self.testForLowerSampleMean(self.gyro, self.air_range, self.landing_range, print_out=print_out, header='Test gyro mean (air time < landing time)'),
            self.testForLargerSampleStdDev(self.mG, self.landing_range, print_out=print_out, header='Test mG std dev (landing time > pop)'),
            self.testForLargerSampleStdDev(self.gyro, self.landing_range, print_out=print_out, header='Test gyro std dev (landing time > pop)'),
            self.testForLargerSampleMean(self.mG, self.landing_range, print_out=print_out, header='Test mG mean (landing time > pop)'),
            self.testForLargerSampleMean(self.gyro, self.landing_range, print_out=print_out, header='Test gyro mean (landing time > pop)'),
            self.testForLargeImpulse(self.mG, self.air_range, print_out=print_out, header='Test landing time mG contains large impulse > (3 * std dev)')
        ]
    

    def test(self, print_out=False):
        """Runs the internal test suite to determine the confidence value of the jump identification.
        Currently, all tests are weighted equally.
        
        Returns the number of tests passed, total tests, and the confidence value in %.
        """
        results = self.runTestSuite(print_out=print_out)
        self.tests_passed = sum([int(r) for r in results])
        self.total_tests = len(results)
        self.confidence = self.tests_passed / self.total_tests * 100
    
    
    def identify(self, print_out=False):
        """Identifies the ranges of air time and landing"""
        self.min_idx = minIndex(self.mG_lpf, self.lowG_range)
        if print_out: print('min_idx:\t\t', self.min_idx)

        # TODO confirm jump alignment

        self.computeAirPhase(print_out=print_out)
        self.computeLandingPhase(print_out=print_out)
        self.test(print_out=print_out)
    
