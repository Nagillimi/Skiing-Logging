import numpy as np


class EvaluatedKinematics:
    def __init__(self) -> None:
        self.confidence = 0.
        self.tests_passed = 0
        self.total_tests = 0


    def test(self, suite, print_out=False):
        """Runs the child test suite to determine the confidence value of the specific kinematic estimation.
        
        Currently, all tests are weighted equally.
        """
        results = suite(print_out=print_out)
        self.tests_passed = np.sum(results)
        self.total_tests = results.shape[0]
        self.confidence = self.tests_passed / self.total_tests * 100
    

    @property
    def confidence(self) -> float:
        """Confidence value, sum of passed tests / total tests."""
        return self.__confidence
    
    @confidence.setter
    def confidence(self, confidence):
        self.__confidence = confidence


    @property
    def tests_passed(self) -> int:
        """Number of passed tests."""
        return self.__tests_passed
    
    @tests_passed.setter
    def tests_passed(self, tests_passed):
        self.__tests_passed = tests_passed


    @property
    def total_tests(self) -> int:
        """Total number of tests."""
        return self.__total_tests
    
    @total_tests.setter
    def total_tests(self, total_tests):
        self.__total_tests = total_tests