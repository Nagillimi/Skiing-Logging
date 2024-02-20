import numpy as np
from domain.session_logger import SessionLogger as logger
from utilities.decorators.print_test_results import printTestResults
from utilities.sig_proc_np import maxIndex


class StatTests:
    @staticmethod
    def assertWindow(x: np.ndarray, r=[0, -1]):
        if not x.ndim == 1:
            return x, False
        window = x[r[0]:r[1]]
        if window.shape[0] <= 0:
            return window, False
        return window, True


    @printTestResults
    @staticmethod
    def testContainsLocalPeak(x: np.ndarray, r=[0, -1], header=""):
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
        logger.debug(f'\t\t{head} < {max_window} < {tail}?')
        if head < max_window and max_window > tail:
            return True
        return False


    @printTestResults
    @staticmethod
    def testDecreasingTrend(x: np.ndarray, r=[0, -1], th=1, header=""):
        """tests the input `x` signal for an overall decreasing trend
        
        if so, returns `True` else `False`
        """
        window, isValid = StatTests.assertWindow(x, r)
        if not isValid:
            return False
        
        for i in range(window.shape[0] - 1):
            # logger.debug(f'\t\t{window[i + 1]} - {window[i]} = {window[i + 1] - window[i]} < {th}?')
            if (window[i + 1] - window[i]) > th:
                return False
        return True


    @printTestResults
    @staticmethod
    def testMinSampleCount(r=[0, -1], min_count=50, header=""):
        samples = r[1] - r[0]
        logger.debug(f'\t\t{samples} >= {min_count}?')
        if samples >= min_count: 
            return True
        return False
    

    @printTestResults
    @staticmethod
    def testLowerSampleStdDev(x: np.ndarray, r=[0, -1], against_other_r=None, header=""):
        """tests the input `x` signal for a smaller sample standard deviation vs the population.
        
        Unless `against_other_r` is passed, where the sample will test against it instead.
        """
        window, isValid = StatTests.assertWindow(x, r)
        if not isValid:
            return False
        
        sample_against = x if against_other_r is None else x[against_other_r[0]:against_other_r[1]]
        logger.debug(f'\t\t{np.std(window)} < {np.std(sample_against)}?')
        if np.std(window) < np.std(sample_against):
            return True
        return False


    @printTestResults
    @staticmethod
    def testLargerSampleStdDev(x: np.ndarray, r=[0, -1], against_other_r=None, header=""):
        """tests the input `x` signal for a larger sample standard deviation vs the population.
        
        Unless `against_other_r` is passed, where the sample will test against it instead.
        """
        window, isValid = StatTests.assertWindow(x, r)
        if not isValid:
            return False
        
        sample_against = x if against_other_r is None else x[against_other_r[0]:against_other_r[1]]
        logger.debug(f'\t\t{np.std(window)} > {np.std(sample_against)}?')
        if np.std(window) > np.std(sample_against):
            return True
        return False


    @printTestResults
    @staticmethod
    def testLowerSampleMean(x: np.ndarray, r=[0, -1], against_other_r=None, header=""):
        """tests the input `x` signal for a smaller sample mean vs the population.
        
        Unless `against_other_r` is passed, where the sample will test against it instead.
        """
        window, isValid = StatTests.assertWindow(x, r)
        if not isValid:
            return False
        
        sample_against = x if against_other_r is None else x[against_other_r[0]:against_other_r[1]]
        logger.debug(f'\t\t{np.mean(window)} < {np.mean(sample_against)}?')
        if np.mean(window) < np.mean(sample_against):
            return True
        return False


    @printTestResults
    @staticmethod
    def testLargerSampleMean(x: np.ndarray, r=[0, -1], against_other_r=None, header=""):
        """tests the input `x` signal for a larger sample mean vs the population.
        
        Unless `against_other_r` is passed, where the sample will test against it instead.
        """
        window, isValid = StatTests.assertWindow(x, r)
        if not isValid:
            return False
        
        sample_against = x if against_other_r is None else x[against_other_r[0]:against_other_r[1]]
        logger.debug(f'\t\t{np.mean(window)} > {np.mean(sample_against)}?')
        if np.mean(window) > np.mean(sample_against):
            return True
        return False


    @printTestResults
    @staticmethod
    def testLargestMagnitude(x: np.ndarray, r=[0, -1], override_max=None, th=None, header=""):
        """tests the input `x` signal whether a large impulse occured during the range `r`.
        
        `th` will override the threshold of the impulse magnitude test, defaults to 3 * stddev
        """
        window, isValid = StatTests.assertWindow(x, r)
        if not isValid:
            return False
        
        baseline = 3 * np.std(window) if th is None else th
        impulse = np.max(window) if override_max is None else override_max
        logger.debug(f'\t\t{impulse} > {baseline}?')
        if impulse > baseline:
            return True
        return False


    @printTestResults
    @staticmethod
    def testSmallestMagnitude(x: np.ndarray, r=[0, -1], th=None, header=""):
        """tests the input `x` signal whether a small magnitude occured during the range `r`.
        
        `th` will override the threshold of the impulse magnitude test, defaults to (1 / 3) * stddev
        """
        window, isValid = StatTests.assertWindow(x, r)
        if not isValid:
            return False
        
        baseline = (1 / 3) * np.std(window) if th is None else th
        smallest_mag = np.min(window)
        logger.debug(f'\t\t{smallest_mag} < {baseline}?')
        if smallest_mag < baseline:
            return True
        return False


    @printTestResults
    @staticmethod
    def testTimingOfMagnitude(x: np.ndarray, r=[0, -1], th=None, header=""):
        """tests the input `x` signal whether a large impulse occured close to the start of the landing range.
        
        `th` will override the threshold of the impulse magnitude test, defaults to 3 * stddev
        """
        window, isValid = StatTests.assertWindow(x, r)
        if not isValid:
            return False

        min_samples = 20 if th is None else th
        impulse_idx = maxIndex(window) + 1
        logger.debug(f'\t\t{impulse_idx} < {min_samples}?')
        if impulse_idx < min_samples:
            return True
        return False


    @printTestResults
    @staticmethod
    def testRecentMax(x: np.ndarray, r=[0, -1], th=None, header=""):
        """tests the input `x` signal whether a large impulse occured close to the start of the landing range.
        
        `th` will override the threshold of the impulse magnitude test, defaults to 3 * stddev
        """
        window, isValid = StatTests.assertWindow(x, r)
        if not isValid:
            return False

        L = window.shape[0]
        min_samples = 20 if th is None else th
        max_idx = maxIndex(window) + 1
        logger.debug(f'\t\t{L} - {max_idx} < {min_samples}?')
        if L - max_idx < min_samples:
            return True
        return False
