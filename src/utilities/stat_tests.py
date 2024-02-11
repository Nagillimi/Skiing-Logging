import numpy as np
from utilities.decorators import printTestResults
from utilities.sig_proc_np import maxIndex


class StatTests:
    @staticmethod
    def assertWindow(x: np.ndarray, r: list):
        if not x.ndim == 1:
            return x, False
        window = x[r[0]:r[1]]
        if not window.shape[0] > 0:
            return window, False
        return window, True


    @printTestResults
    @staticmethod
    def testContainsLocalPeak(x: np.ndarray, r: list, print_out=False, header=""):
        """tests the input `x` signal for a peak inside the range `r`, excluding the endponits.

        The max will need to be higher than `th` which is default to `5`
        
        if so, returns `True` else `False`
        """
        window, isValid = StatTests.assertWindow(x, r)
        if not isValid:
            return False

        max_window = np.max(window)
        head = x[r[0]]
        tail = x[r[1]]
        if print_out: print('\t', head, ' < ', max_window, ' < ', tail, '?', sep='')
        if head < max_window and max_window > tail:
            return True
        return False


    @printTestResults
    @staticmethod
    def testDecreasingTrend(x: np.ndarray, r: list, th=1, print_out=False, header=""):
        """tests the input `x` signal for an overall decreasing trend
        
        if so, returns `True` else `False`
        """
        window, isValid = StatTests.assertWindow(x, r)
        if not isValid:
            return False
        
        for i in range(window.shape[0] - 1):
            if print_out: print('\t', window[i + 1], '-', window[i], '=', window[i + 1] - window[i], ' > ', th, '?', sep='')
            if window[i + 1] - window[i] > th:
                return False
        return True


    @printTestResults
    @staticmethod
    def testMinSampleCount(x: np.ndarray, r: list, min_count=50, print_out=False, header=""):
        window, isValid = StatTests.assertWindow(x, r)
        if not isValid:
            return False
        
        samples = window.shape[0]
        if print_out: print('\t', samples, ' >= ', min_count, '?', sep='')
        if samples >= min_count: 
            return True
        return False
    

    @printTestResults
    @staticmethod
    def testLowerSampleStdDev(x: np.ndarray, r: list, against_other_r=None, print_out=False, header=""):
        """tests the input `x` signal for a smaller sample standard deviation vs the population.
        
        Unless `against_other_r` is passed, where the sample will test against it instead.
        """
        window, isValid = StatTests.assertWindow(x, r)
        if not isValid:
            return False
        
        sample_against = x if against_other_r is None else x[against_other_r[0]:against_other_r[1]]
        if print_out: print('\t', np.std(window), ' < ', np.std(sample_against), '?', sep='')
        if np.std(window) < np.std(sample_against):
            return True
        return False


    @printTestResults
    @staticmethod
    def testLargerSampleStdDev(x: np.ndarray, r: list, against_other_r=None, print_out=False, header=""):
        """tests the input `x` signal for a larger sample standard deviation vs the population.
        
        Unless `against_other_r` is passed, where the sample will test against it instead.
        """
        window, isValid = StatTests.assertWindow(x, r)
        if not isValid:
            return False
        
        sample_against = x if against_other_r is None else x[against_other_r[0]:against_other_r[1]]
        if print_out: print('\t', np.std(window), ' > ', np.std(sample_against), '?', sep='')
        if np.std(window) > np.std(sample_against):
            return True
        return False


    @printTestResults
    @staticmethod
    def testLowerSampleMean(x: np.ndarray, r: list, against_other_r=None, print_out=False, header=""):
        """tests the input `x` signal for a smaller sample mean vs the population.
        
        Unless `against_other_r` is passed, where the sample will test against it instead.
        """
        window, isValid = StatTests.assertWindow(x, r)
        if not isValid:
            return False
        
        sample_against = x if against_other_r is None else x[against_other_r[0]:against_other_r[1]]
        if print_out: print('\t', np.mean(window), ' < ', np.mean(sample_against), '?', sep='')
        if np.mean(window) < np.mean(sample_against):
            return True
        return False


    @printTestResults
    @staticmethod
    def testLargerSampleMean(x: np.ndarray, r: list, against_other_r=None, print_out=False, header=""):
        """tests the input `x` signal for a larger sample mean vs the population.
        
        Unless `against_other_r` is passed, where the sample will test against it instead.
        """
        window, isValid = StatTests.assertWindow(x, r)
        if not isValid:
            return False
        
        sample_against = x if against_other_r is None else x[against_other_r[0]:against_other_r[1]]
        if print_out: print('\t', np.mean(window), ' > ', np.mean(sample_against), '?', sep='')
        if np.mean(window) > np.mean(sample_against):
            return True
        return False


    @printTestResults
    @staticmethod
    def testLargeImpulse(x: np.ndarray, r: list, override_max=None, th=None, print_out=False, header=""):
        """tests the input `x` signal whether a large impulse occured during the range `r`.
        
        `th` will override the threshold of the impulse magnitude test, defaults to 3 * stddev
        """
        window, isValid = StatTests.assertWindow(x, r)
        if not isValid:
            return False
        
        baseline = 3 * np.std(window) if th is None else th
        impulse = np.max(window) if override_max is None else override_max
        if print_out: print('\t', impulse, ' > ', baseline, '?', sep='')
        if impulse > baseline:
            return True
        return False


    @printTestResults
    @staticmethod
    def testTimingOfLargeImpulse(x: np.ndarray, r: list, th=None, print_out=False, header=""):
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
