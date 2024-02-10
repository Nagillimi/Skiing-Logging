import math
from scipy import signal


def arma(x: list, m=5):
    """Autoregressive Moving-Average digital IIR filter, can be used LP, HP, and BP.
    
    https://en.wikibooks.org/wiki/Signal_Processing/Digital_Filters#ARMA_Filters
    """


def butter(x: list, m=2):
    """"""


def diff(x1: list, x2: list):
    """returns `x1` - `x2` element-wise."""
    return [x1[i] - x2[i] for i in range(len(x1))]


def makeContinuousRange(x: list, m=0.5, full_scale=360, print_out=False):
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
    N = len(x)
    m_FS = m * full_scale
    p = 0
    if print_out: print('Making signal continuous based on FS range:', full_scale)

    for i in range(N):
        if i == 0: continue
        if print_out:
            current_p = round(i/N*100)
            if current_p % 5 == 0 and p != current_p:
                print('makeContinuousRange() progress', current_p, '%')
                p = current_p

        xi_minus_xi1 = x[i] - x[i - 1]
        abs_xi_minus_xi1 = abs(xi_minus_xi1)

        if xi_minus_xi1 > 0 and abs_xi_minus_xi1 >= m_FS:
            skips.append([i - 1, i])
            for j in range(N - i):
                y[i + j] = x[i + j] - full_scale
                if xi_minus_xi1 < 0 and abs_xi_minus_xi1 >= m_FS:
                    skips.append([i - 1, i])
                    break
            continue

        if xi_minus_xi1 < 0 and abs_xi_minus_xi1 >= m_FS:
            skips.append([i - 1, i])
            for j in range(N - i):
                y[i + j] = x[i + j] + full_scale
                if xi_minus_xi1 > 0 and abs_xi_minus_xi1 >= m_FS:
                    skips.append([i - 1, i])
                    break
            continue
    if print_out: print('makeContinuousRange() skips found:', len(skips))
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


def makeContinuousRange3dof(x: list, fix_0=True, fix_1=True, fix_2=True):
    """Runs `fixZeroCrossing()` for each column signal in the input ndarray `x`
    
    Returns the ndarray, with fixed zero crossings on each column signal individually.
    """
    rollFix, roll_skips = makeContinuousRange(x[0], full_scale=180)
    pitchFix, pitch_skips = makeContinuousRange(x[1], full_scale=180)
    yawFix, yaw_skips = makeContinuousRange(x[2])
    return [
        rollFix if len(roll_skips) > 0 and fix_0 is True else x[0],
        pitchFix if len(pitch_skips) > 0 and fix_1 is True else x[1],
        yawFix if len(yaw_skips) > 0 and fix_2 is True else x[2],
    ]


def groupClosePointsIntoRanges(idxs: list, th=2):
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


def identifyRangesBelowTH(x: list, th):
    idxs = idxsUnderTH(x, th)
    return groupClosePointsIntoRanges(idxs)


def idxsUnderTH(x: list, th=200):
    """Return a list of indicies of the input signal `x` whose elements fall
    below `th`.
    """
    return [x.index(xi) for xi in x if xi < th]


def length(ax: list, ay: list, az: list):
    """Computes the vector length based on the `x`, `y`, `z` components"""
    return [math.sqrt(ax[i]**2 + ay[i]**2 + az[i]**2) for i in range(len(ax))]


def lowpass(x: list, Wn, ftype='iir1'):
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



def mae(x1: list, x2: list):
    """Mean absolute error between `x1` and `x2`."""
    d = diff(x1, x2)
    abs_d = [abs(di) for di in d]
    return mean(abs_d)


def maxIndex(x: list, r=None):
    """Population max index with of input signal `x`"""
    if len(x) == 0:
        return -1
    if r is None:
        return x.index(max(x))
    if r[0] == r[1]:
        return r[0]
    window = x[r[0]:r[1]]
    return r[0] + window.index(max(window))


def mean(x: list):
    """Population mean of the full range of input signal `x`"""
    return sum(x) / (len(x) if len(x) > 0 else 1)


def mse(x1: list, x2: list):
    """Mean sum error between `x1` and `x2`."""
    d = diff(x1, x2)
    d2 = [di**2 for di in d]
    return mean(d2)


def minIndex(x: list, r=None):
    """Population min index with of input signal `x`"""
    if len(x) == 0:
        return -1
    if r is None:
        return x.index(min(x))
    if r[0] == r[1]:
        return r[0]
    window = x[r[0]:r[1]]
    return r[0] + window.index(min(window))


def rmse(x1: list, x2: list):
    """Root mean sum error between `x1` and `x2`."""
    return math.sqrt(mse(x1, x2))


def std(x: list):
    """Population standard deviation of the full range of input signal `x`"""
    return math.sqrt(variance(x))


def cumtrapz(x: list, dt=0.01):
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


def variance(x: list):
    """Population variance
    `sum((xi - mean(x))**2) / len(x)`
    """
    u = mean(x)
    return sum([(xi - u)**2 for xi in x]) / (len(x) if len(x) > 0 else 1)
