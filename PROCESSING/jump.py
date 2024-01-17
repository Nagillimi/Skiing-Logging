from jump_tests import JumpTests
from signal_processing import maxIndex, minIndex

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
    def mgThreshold():
        """The static low mG threshold to trigger jump identification."""
        return 600


    def computeAirRange(self, th=2, print_out=False):
        """Calculate the index range of total air time, where `min_idx` is the last element.
        
        Scans the left of `mG_lpf` signal for start of the decline to the min_index of low G.
        """
        x1 = 0
        for i in range(len(self.mG_lpf[0:self.min_idx])):
            if self.mG_lpf[self.min_idx - i] - self.mG_lpf[self.min_idx - (i + 1)] > th:
                x1 = self.min_idx - (i + 1)
                break
        self.air_range =  [maxIndex(self.mG_lpf, [x1, self.min_idx]), self.min_idx]
        if print_out: print('air_range:\t', self.air_range)
    

    def computeLandingRange(self, delay_s=0.5, print_out=False):
        """Calculate the index range of the landing phase, where `min_idx` is the first element.
        
        Uses a static delay of `delay_s` after a small increase is observed in the `mG_lpf`.
        """
        touch_idx = 0
        for i in range(len(self.mg_lpf[self.min_idx:-1])):
            if self.mg_lpf[self.min_idx + (i + 1)] - self.mg_lpf[self.min_idx + i] > 10:
                touch_idx = self.min_idx + i + 1
                break

        x2 = int(touch_idx + delay_s * 100)
        self.landing_range = [self.min_idx, maxIndex(self.mg_lpf, [self.min_idx, x2])]
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
        self.min_index = minIndex(self.mG_lpf, self.lowG_range)
        if print_out: print('min_index:\t\t', self.min_index)

        self.computeAirRange(print_out=print_out)
        self.computeLandingRange(print_out=print_out)

        # TODO: methods for determining air time and distance

        self.test(print_out=print_out)
    
