import numpy as np
from utilities.stat_tests import StatTests as ST

class Turn:
    def __init__(self,
            mG_lpf: np.ndarray,
            roll: np.ndarray,
            yaw: np.ndarray,
            print_out=False
    ) -> None:
        self.mG_lpf = mG_lpf
        self.roll = roll
        self.yaw = yaw
        self.confidence = 0.
        self.tests_passed = 0
        self.total_tests = 0

        self.identify(print_out=print_out)


    def runTestSuite(self, print_out=False) -> np.ndarray:
        """Run the test suite. Can toggle individual running here.
        
        In the future, can return values and parameters for each test. For ML
        """
        return np.array([
            
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
        """"""
        self.test(print_out=print_out)


    @property
    def side(self) -> str:
        """Side of turn (`left` or `right`)."""
        return self.__side

    @side.setter
    def side(self, side):
        self.__side = side