from decorators import printTestResults
from signal_processing import mean, std

class JumpTests:
    def __init__(self) -> None:
        pass


    @printTestResults
    def testForDecreasingTrend(self, x, r, th=1, print_out=False, header=""):
        """tests the input `x` signal for an overall decreasing trend
        
        if so, returns `True` else `False`
        """
        window = x[r[0]:r[1]]
        for i in range(len(window) - 1):
            if print_out: print('\t', window[i + 1], '-', window[i], '=', window[i + 1] - window[i], ' > ', th, '?', sep='')
            if window[i + 1] - window[i] > th:
                return False
        return True


    @printTestResults
    def testForMinSampleCount(self, x, r, th=50, print_out=False, header=""):
        samples = r[1] - r[0]
        if print_out: print('\t', samples, ' >= ', th, '?', sep='')
        if samples >= th: 
            return True
        return False


    @printTestResults
    def testForLowerSampleStdDev(self, x, r, against_other_r=None, print_out=False, header=""):
        """tests the input `x` signal for a smaller sample standard deviation vs the population.
        
        Unless `against_other_r` is passed, where the sample will test against it instead.
        """
        window = x[r[0]:r[1]]
        sample_against = x if against_other_r is None else x[against_other_r[0]:against_other_r[1]]
        if print_out: print('\t', std(window), ' < ', std(sample_against), '?', sep='')
        if std(window) < std(sample_against):
            return True
        return False


    @printTestResults
    def testForLargerSampleStdDev(self, x, r, against_other_r=None, print_out=False, header=""):
        """tests the input `x` signal for a larger sample standard deviation vs the population.
        
        Unless `against_other_r` is passed, where the sample will test against it instead.
        """
        window = x[r[0]:r[1]]
        sample_against = x if against_other_r is None else x[against_other_r[0]:against_other_r[1]]
        if print_out: print('\t', std(window), ' > ', std(sample_against), '?', sep='')
        if std(window) > std(sample_against):
            return True
        return False


    @printTestResults
    def testForLowerSampleMean(self, x, r, against_other_r=None, print_out=False, header=""):
        """tests the input `x` signal for a smaller sample mean vs the population.
        
        Unless `against_other_r` is passed, where the sample will test against it instead.
        """
        window = x[r[0]:r[1]]
        sample_against = x if against_other_r is None else x[against_other_r[0]:against_other_r[1]]
        if print_out: print('\t', mean(window), ' < ', mean(sample_against), '?', sep='')
        if mean(window) < mean(sample_against):
            return True
        return False


    @printTestResults
    def testForLargerSampleMean(self, x, r, against_other_r=None, print_out=False, header=""):
        """tests the input `x` signal for a larger sample mean vs the population.
        
        Unless `against_other_r` is passed, where the sample will test against it instead.
        """
        window = x[r[0]:r[1]]
        sample_against = x if against_other_r is None else x[against_other_r[0]:against_other_r[1]]
        if print_out: print('\t', mean(window), ' > ', mean(sample_against), '?', sep='')
        if mean(window) > mean(sample_against):
            return True
        return False


    @printTestResults
    def testForLargeImpulse(self, x, r, override_max=None, th=None, print_out=False, header=""):
        """tests the input `x` signal whether a large impulse occured during the range `r`.
        
        `th` will override the threshold of the impulse magnitude test, defaults self, to 3 * stddev
        """
        window = x[r[0]:r[1]]
        baseline = 3 * std(window) if th is None else th
        impulse = max(window) if override_max is None else override_max
        if print_out: print('\t', impulse, ' > ', baseline, '?', sep='')
        if impulse > baseline:
            return True
        return False
