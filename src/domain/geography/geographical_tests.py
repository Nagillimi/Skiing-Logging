
class GeographicalSearchTestingParameters:
    def __init__(
            self, 
            x,
            within_s,
            window_s,
    ) -> None:
        self.fs = 100
        self.x = x
        self.within_s = within_s
        self.window_s = window_s


class GeographicalTest:
    def test(self, i: int) -> bool: {}


class DecreasingSlopeGTTh(GeographicalTest):
    def __init__(self, th) -> None:
        self.th = th

    def test(self, params: GeographicalSearchTestingParameters, i) -> bool:
        fs = params.fs
        x = params.x
        within_s = params.within_s

        return x[i - (within_s * fs)] - x[i] > self.th


class DecreasingSlopeLTTh(GeographicalTest):
    def __init__(self, th) -> None:
        self.th = th

    def test(self, params: GeographicalSearchTestingParameters, i) -> bool:
        fs = params.fs
        x = params.x
        within_s = params.within_s

        return x[i - (within_s * fs)] - x[i] < self.th and x[i - (within_s * fs)] - x[i] > 0


class IncreasingSlopeGTTh(GeographicalTest):
    def __init__(self, th) -> None:
        self.th = th

    def test(self, params: GeographicalSearchTestingParameters, i) -> bool:
        fs = params.fs
        x = params.x
        within_s = params.within_s

        return x[i - (within_s * fs)] - x[i] < -self.th


class IncreasingSlopeLTTh(GeographicalTest):
    def __init__(self, th) -> None:
        self.th = th

    def test(self, params: GeographicalSearchTestingParameters, i) -> bool:
        fs = params.fs
        x = params.x
        within_s = params.within_s

        return x[i - (within_s * fs)] - x[i] > -self.th and x[i] - x[i - (within_s * fs)] < 0


class MaxAtBeginningOfPeriod(GeographicalTest):
    def test(self, params: GeographicalSearchTestingParameters, i) -> bool:
        fs = params.fs
        x = params.x
        within_s = params.within_s
        window_s = params.window_s

        return x[i - (within_s * fs)] == max(x[i - (window_s * fs):i])


class MinAtBeginningOfPeriod(GeographicalTest):
    def test(self, params: GeographicalSearchTestingParameters, i) -> bool:
        fs = params.fs
        x = params.x
        within_s = params.within_s
        window_s = params.window_s

        return x[i - (within_s * fs)] == min(x[i - (window_s * fs):i])


class SlopeRangeGTTh(GeographicalTest):
    def __init__(self, th) -> None:
        self.th = th

    def test(self, params: GeographicalSearchTestingParameters, i) -> bool:
        fs = params.fs
        x = params.x
        window_s = params.window_s

        return max(x[i - (window_s * fs):i]) - min(x[i - (window_s * fs):i]) > self.th


class CurrentMaxWithinPeriod(GeographicalTest):
    def test(self, params: GeographicalSearchTestingParameters, i) -> bool:
        fs = params.fs
        x = params.x
        window_s = params.window_s

        return x[i] == max(x[i - (window_s * fs):i])


class CurrentMinWithinPeriod(GeographicalTest):
    def test(self, params: GeographicalSearchTestingParameters, i) -> bool:
        fs = params.fs
        x = params.x
        window_s = params.window_s

        return x[i] == min(x[i - (window_s * fs):i])

