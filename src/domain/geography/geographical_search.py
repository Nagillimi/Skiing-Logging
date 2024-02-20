import numpy as np
from domain.geography.geographical_tests import GeographicalTest, GeographicalSearchTestingParameters


class GeographicalSearch:
    """
    Performs a search based on the input signal `x`, performing the attached tests and 
    returning the intersecting index that all tests satisfy.

    Parameters
    ----------

    `dx`    The step size, determines how coarse the search is. Dependent on the accuracy of the 
            point you wish to id

    `within_s`  The main comparison window used for increasing/decreasing trends. Since this is causal,
            i - within_s*fs is the actual index returned in the id. In seconds.

    `window_s`  The secondary comparison window used for increasing/decreasing trends. Used to confirm 
            larger trends compared to the id'd index from `within_s`. In seconds.

    """
    def __init__(
            self, 
            x: np.ndarray,
            dx: int,
            within_s: int,
            window_s: int,
            tests: list[GeographicalTest],
    ) -> None:
        self.search_params = GeographicalSearchTestingParameters(
            x=x,
            within_s=within_s,
            window_s=window_s,
        )
        self.x = x
        self.dx = dx
        self.tests = tests


    def search(self, min_idx) -> int | None:
        """Search method that splices the windowed signal and performs the attached tests.
        
        If the tests all return True, the index is returned, otherwise `None` if it's never met.
        """
        xw = self.search_params.x[min_idx:]
        for i in range(int(xw.shape[0] / self.dx)):
            i *= self.dx

            if i < max(self.search_params.window_s, self.search_params.within_s) * self.search_params.fs:
                continue

            if all([
                test_in_tester.test(self.search_params, min_idx + i)
                for test_in_tester in self.tests
            ]):
                return min_idx + i - (self.search_params.within_s * self.search_params.fs)
            
        return None

