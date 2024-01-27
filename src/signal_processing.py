import math
from scipy import signal
import numpy as np


def arma(x, m=5):
    """Autoregressive Moving-Average digital IIR filter, can be used LP, HP, and BP.
    
    https://en.wikibooks.org/wiki/Signal_Processing/Digital_Filters#ARMA_Filters
    """


def butter(x, m=2):
    """"""


def diff(x1, x2):
    """returns `x1` - `x2` element-wise."""
    return [x1[i] - x2[i] for i in range(len(x1))]


def makeContinuousRange(x, m=0.5, full_scale=360):
    """Fixes the zero crossings in a signal that is previously clamped to a 
    single scale range of `single_scale`.

    Note, this can get out of control if you keep on turning around and around (for a yaw example).
    The numbers will just keep increasing until you come back to baseline.

    This is useful for graphs when trying to test for stillness, since a zero crossing would be a massive
    outlier.

    Returns
    -------
    unclamped signal `x` and the observed skipping indices
    """
    y = x
    skips = []
    for i in range(len(x)):
        if i == 0: continue
        if x[i] > x[i - 1] and abs(x[i] - x[i - 1]) >= (m * full_scale):
            skips.append([i - 1, i])
            for j in range(len(x) - i):
                y[i + j] = x[i + j] - full_scale
                if x[i] < x[i - 1] and abs(x[i] - x[i - 1]) >= (m * full_scale):
                    skips.append([i - 1, i])
                    break
            continue

        if x[i] < x[i - 1] and abs(x[i] - x[i - 1]) >= (m * full_scale):
            skips.append([i - 1, i])
            for j in range(len(x) - i):
                y[i + j] = x[i + j] + full_scale
                if x[i] > x[i - 1] and abs(x[i] - x[i - 1]) >= (m * full_scale):
                    skips.append([i - 1, i])
                    break
            continue
    return y, skips

    # print(len(x))
    # m = 0.95
    # y = x
    # for i in range(len(x) - 1):
    #     # if i == 0: continue
    #     y[i] = x[i] + c
    #     if x[i + 1] > 0 and (x[i + 1] - x[i]) >= (m * full_scale):
    #         fixZeroCrossings(x[i + 1:], -full_scale)

    #     if x[i + 1] < 0 and (x[i + 1] - x[i]) <= -(m * full_scale):
    #         fixZeroCrossings(x[i + 1:], full_scale)
    # return y


def makeContinuousRange3dof(x, fix_0=True, fix_1=True, fix_2=True):
    """Runs `fixZeroCrossing()` for each column signal in the input ndarray `x`
    
    Returns the ndarray, with fixed zero crossings on each column signal individually.
    """
    rollFix, roll_skips = makeContinuousRange(x[:, 0].tolist(), full_scale=180)
    pitchFix, pitch_skips = makeContinuousRange(x[:, 1].tolist(), full_scale=180)
    yawFix, yaw_skips = makeContinuousRange(x[:, 2].tolist())
    return np.transpose([
        np.array(rollFix) if len(roll_skips) > 0 and fix_0 is True else x[:, 0],
        np.array(pitchFix) if len(pitch_skips) > 0 and fix_1 is True else x[:, 1],
        np.array(yawFix) if len(yaw_skips) > 0 and fix_2 is True else x[:, 2],
    ])


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


def mae(x1, x2):
    """Mean absolute error between `x1` and `x2`."""
    d = diff(x1, x2)
    abs_d = [abs(di) for di in d]
    return mean(abs_d)


def maxIndex(x, r=None):
    """Population max index with of input signal `x`"""
    if r is None:
        return x.index(max(x))
    if r[0] == r[1]:
        return r[0]
    window = x[r[0]:r[1]]
    return r[0] + window.index(max(window))


def mean(x):
    """Population mean of the full range of input signal `x`"""
    return sum(x) / (len(x) if len(x) > 0 else 1)


def mse(x1, x2):
    """Mean sum error between `x1` and `x2`."""
    d = diff(x1, x2)
    d2 = [di**2 for di in d]
    return mean(d2)


def minIndex(x, r=None):
    """Population min index with of input signal `x`"""
    if r is None:
        return x.index(min(x))
    if r[0] == r[1]:
        return r[0]
    window = x[r[0]:r[1]]
    return r[0] + window.index(min(window))


def rmse(x1, x2):
    """Root mean sum error between `x1` and `x2`."""
    return math.sqrt(mse(x1, x2))


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
    return sum([(xi - u)**2 for xi in x]) / (len(x) if len(x) > 0 else 1)
