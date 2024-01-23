from decorators import printTestResults
from signal_processing import mean, std, maxIndex

class StatTests:
    @staticmethod
    def assertWindow(x, r):
        window = x[r[0]:r[1]]
        if not len(window) > 0:
            return window, False
        return window, True


    @printTestResults
    @staticmethod
    def testContainsLocalPeak(x, r, print_out=False, header=""):
        """tests the input `x` signal for a peak inside the range `r`, excluding the endponits.

        The max will need to be higher than `th` which is default to `5`
        
        if so, returns `True` else `False`
        """
        window, isValid = StatTests.assertWindow(x, r)
        if not isValid:
            return False

        max_window = max(window)
        head = x[r[0]]
        tail = x[r[1]]
        spread = max_window - min(window)
        if print_out: print('\t', head, ' < ', max_window, ' < ', tail, '?', sep='')
        if head < max_window and max_window > tail:
            return True
        return False


    @printTestResults
    @staticmethod
    def testDecreasingTrend(x, r, th=1, print_out=False, header=""):
        """tests the input `x` signal for an overall decreasing trend
        
        if so, returns `True` else `False`
        """
        window, isValid = StatTests.assertWindow(x, r)
        if not isValid:
            return False
        
        for i in range(len(window) - 1):
            if print_out: print('\t', window[i + 1], '-', window[i], '=', window[i + 1] - window[i], ' > ', th, '?', sep='')
            if window[i + 1] - window[i] > th:
                return False
        return True


    @printTestResults
    @staticmethod
    def testMinSampleCount(x, r, min_count=50, print_out=False, header=""):
        window, isValid = StatTests.assertWindow(x, r)
        if not isValid:
            return False
        
        samples = len(window)
        if print_out: print('\t', samples, ' >= ', min_count, '?', sep='')
        if samples >= min_count: 
            return True
        return False
    

    @printTestResults
    @staticmethod
    def testLowerSampleStdDev(x, r, against_other_r=None, print_out=False, header=""):
        """tests the input `x` signal for a smaller sample standard deviation vs the population.
        
        Unless `against_other_r` is passed, where the sample will test against it instead.
        """
        window, isValid = StatTests.assertWindow(x, r)
        if not isValid:
            return False
        
        sample_against = x if against_other_r is None else x[against_other_r[0]:against_other_r[1]]
        if print_out: print('\t', std(window), ' < ', std(sample_against), '?', sep='')
        if std(window) < std(sample_against):
            return True
        return False


    @printTestResults
    @staticmethod
    def testLargerSampleStdDev(x, r, against_other_r=None, print_out=False, header=""):
        """tests the input `x` signal for a larger sample standard deviation vs the population.
        
        Unless `against_other_r` is passed, where the sample will test against it instead.
        """
        window, isValid = StatTests.assertWindow(x, r)
        if not isValid:
            return False
        
        sample_against = x if against_other_r is None else x[against_other_r[0]:against_other_r[1]]
        if print_out: print('\t', std(window), ' > ', std(sample_against), '?', sep='')
        if std(window) > std(sample_against):
            return True
        return False


    @printTestResults
    @staticmethod
    def testLowerSampleMean(x, r, against_other_r=None, print_out=False, header=""):
        """tests the input `x` signal for a smaller sample mean vs the population.
        
        Unless `against_other_r` is passed, where the sample will test against it instead.
        """
        window, isValid = StatTests.assertWindow(x, r)
        if not isValid:
            return False
        
        sample_against = x if against_other_r is None else x[against_other_r[0]:against_other_r[1]]
        if print_out: print('\t', mean(window), ' < ', mean(sample_against), '?', sep='')
        if mean(window) < mean(sample_against):
            return True
        return False


    @printTestResults
    @staticmethod
    def testLargerSampleMean(x, r, against_other_r=None, print_out=False, header=""):
        """tests the input `x` signal for a larger sample mean vs the population.
        
        Unless `against_other_r` is passed, where the sample will test against it instead.
        """
        window, isValid = StatTests.assertWindow(x, r)
        if not isValid:
            return False
        
        sample_against = x if against_other_r is None else x[against_other_r[0]:against_other_r[1]]
        if print_out: print('\t', mean(window), ' > ', mean(sample_against), '?', sep='')
        if mean(window) > mean(sample_against):
            return True
        return False


    @printTestResults
    @staticmethod
    def testLargeImpulse(x, r, override_max=None, th=None, print_out=False, header=""):
        """tests the input `x` signal whether a large impulse occured during the range `r`.
        
        `th` will override the threshold of the impulse magnitude test, defaults to 3 * stddev
        """
        window, isValid = StatTests.assertWindow(x, r)
        if not isValid:
            return False
        
        baseline = 3 * std(window) if th is None else th
        impulse = max(window) if override_max is None else override_max
        if print_out: print('\t', impulse, ' > ', baseline, '?', sep='')
        if impulse > baseline:
            return True
        return False


    @printTestResults
    @staticmethod
    def testTimingOfLargeImpulse(x, r, th=None, print_out=False, header=""):
        """tests the input `x` signal whether a large impulse occured close to the start of the landing range.
        
        `th` will override the threshold of the impulse magnitude test, defaults to 3 * stddev
        """
        window, isValid = StatTests.assertWindow(x, r)
        if not isValid:
            return False

        min_samples = 20 if th is None else th
        impulse_idx = maxIndex(window) + 1
        if print_out: print('\t', impulse_idx, ' < ', min_samples, '?', sep='')
        if impulse_idx < min_samples:
            return True
        return False
