import math
from scipy import signal


def arma(x, m=5):
    """Autoregressive Moving-Average digital IIR filter, can be used LP, HP, and BP.
    
    https://en.wikibooks.org/wiki/Signal_Processing/Digital_Filters#ARMA_Filters
    """


def butter(x, m=2):
    """"""


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


def length(ax, ay, az):
    """Computes the vector length based on the `x`, `y`, `z` components"""
    return [math.sqrt(ax[i]**2 + ay[i]**2 + az[i]**2) for i in range(len(ax))]


def lowpass(x, Wn, ftype='iir1'):
    """Lowpass filter input signal `x` by the cutoff frequency `Wn = fc / fs`."""

    if ftype == 'iir1':
        lpfi = x[0]
        lpf = []
        for xi in x: 
            lpfi += Wn * (xi - lpfi)
            lpf.append(lpfi)
        return lpf
    
    elif ftype == 'butter2':
        # b, a = signal.butter(2, Wn, 'low', output='ba')
        # return signal.filtfilt(b, a, x).tolist()

        # prefer 2nd order sections
        sos = signal.butter(2, Wn, 'low', output='sos')
        return signal.sosfiltfilt(sos, x).tolist()
    
    else:
        return []


def maxIndex(x, r):
    """Population max index with of input signal `x`"""
    if len(r) == 0:
        return x.index(max(x))
    if r[0] == r[1]:
        return r[0]
    window = x[r[0]:r[1]]
    return r[0] + window.index(max(window))


def mean(x):
    """Population mean of the full range of input signal `x`"""
    return sum(x) / len(x)


def minIndex(x, r=[]):
    """Population min index with of input signal `x`"""
    if len(r) == 0:
        return x.index(min(x))
    if r[0] == r[1]:
        return r[0]
    window = x[r[0]:r[1]]
    return r[0] + window.index(min(window))


def std(x):
    """Population standard deviation of the full range of input signal `x`"""
    return math.sqrt(variance(x))


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


def variance(x):
    """Population variance
    `sum((xi - mean(x))**2) / len(x)`
    """
    u = mean(x)
    return sum([(xi - u)**2 for xi in x]) / len(x)
