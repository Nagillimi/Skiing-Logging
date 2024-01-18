import math

def groupClosePointsIntoRanges(idxs, th=2):
    """Return list of ranges of sequential points grouped by closeness,
    whose changes are separated by values greater than `th`
    """
    ranges = []
    if len(idxs) == 0:
        return ranges
    x1 = idxs[0]
    x2 = idxs[-1]
    for i in range(len(idxs) - 1):
        if idxs[i + 1] - idxs[i] > th:
            ranges.append([x1, idxs[i]])
            x1 = idxs[i + 1]
    ranges.append([x1, x2])
    return ranges


def identifyRangesBelowTH(x, th):
    idxs = idxsUnderTH(x, th)
    return groupClosePointsIntoRanges(idxs)


def idxsUnderTH(x, th=200):
    """Return a list of indicies of the input signal `x` whose elements fall
    below `th`.
    """
    return [x.index(xi) for xi in x if xi < th]


def trapz(x, dt=0.01):
    """Computes the trapezoidal integration of the input signal `x`.
    
    Assumes a `dt` of 0.01seconds = 100Hz, otherwise override it.
    """
    return [
        (
            # rectangle
            x[i] +
            # triangle
            ((x[i + 1] - (x[i - 1] if i > 0 else 0)) / 2)
        ) * dt for i in range(len(x) - 1)
    ]


def length(ax, ay, az):
    """Computes the vector length based on the `x`, `y`, `z` components"""
    return [math.sqrt(ax[i]**2 + ay[i]**2 + az[i]**2) for i in range(len(ax))]


def lowpass(x, fc, fs=100):
    """Lowpass filter input signal `x` by the cutoff frequency `fc`.
    
    Assume a sampling frequcny of 100Hz, otherwise override `fs`
    """
    delta_t = 1 / fs
    lpfi = x[0]
    lpf = []
    for xi in x: 
        lpfi += fc * (xi - lpfi) * delta_t
        lpf.append(lpfi)
    return lpf


def maxIndex(x, r):
    """Population max index with of input signal `x`"""
    if r[0] == r[1]: return r[0]
    window = x[r[0]:r[1]]
    return r[0] + window.index(max(window))


def mean(x):
    """Population mean of the full range of input signal `x`"""
    return sum(x) / len(x)


def minIndex(x, r):
    """Population min index with of input signal `x`"""
    if r[0] == r[1]: return r[0]
    window = x[r[0]:r[1]]
    return r[0] + window.index(min(window))


def std(x):
    """Population standard deviation of the full range of input signal `x`"""
    return math.sqrt(variance(x))


def variance(x):
    """Population variance
    `sum((xi - mean(x))**2) / len(x)`
    """
    u = mean(x)
    return sum([(xi - u)**2 for xi in x]) / len(x)
