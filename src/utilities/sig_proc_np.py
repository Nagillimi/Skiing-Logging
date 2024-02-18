import numpy as np
from scipy import signal
from domain.session_logger import SessionLogger as logger
from utilities.sig_proc import makeContinuousRange

def onlyIdxsInsideRanges(idxs: np.ndarray, ranges: np.ndarray) -> np.ndarray:
    _idxs = []

    if idxs.ndim == 2:
        for i in range(idxs.shape[0]):
            for j in range(ranges.shape[0]):
                if (
                    idxs[i, 0] > ranges[j, 0] and
                    idxs[i, 1] > ranges[j, 0] and
                    idxs[i, 0] < ranges[j, 1] and
                    idxs[i, 1] < ranges[j, 1]
                ):
                    _idxs.append([idxs[i, 0], idxs[i, 1]])

    elif idxs.ndim == 1:
        for i in range(idxs.shape[0]):
            for j in range(ranges.shape[0]):
                if (
                    idxs[i] > ranges[j, 0] and
                    idxs[i] < ranges[j, 1] 
                ):
                    _idxs.append(idxs[i])

    return np.array(_idxs)


def deriv(x: np.ndarray, dt, lpf=True) -> np.ndarray:
    """Five point estimation for the first order derivative, centred about xi.

    .. math::
    
    y' = 1/(12dt) [x_{n-2} - 8 * x_{n-1} + 8 * x_{n+1} - x_{n+2}]
    
    Perfroms a butter2 lowpass filter with wn=2/100 since the discrete derivative is inherently
    noise enducing. Override `lpf` if you'd like otherwise.
    """
    xw = x[2:-2]
    W = xw.shape[0]
    if W < 1:
        logger.error('Error calculating derivative. Signal not long enough, must be at least 5 elements.')
        return x
    
    one_twelfth_dt = 1 / (12 * dt)
    two_zeros = [0] + [0]
    yw = two_zeros + [(x[i-2] - 8 * x[i-1] + 8 * x[i+1] - x[i+2]) for i in range(W)] + two_zeros
    y = np.divide(yw, one_twelfth_dt)
    return lowpass(y, 2/100) if lpf else y


def groupClosePointsIntoRanges(idxs: np.ndarray, th=2):
    """Return np.ndarray of ranges of sequential points grouped by closeness,
    whose changes are separated by values greater than `th`
    """
    ranges = []
    if len(idxs) == 0:
        return np.zeros((0, 0))
    x1 = idxs[0]
    x2 = idxs[-1]
    for i in range(idxs.shape[0] - 1):
        if idxs[i + 1] - idxs[i] > th:
            ranges.append([x1, idxs[i]])
            x1 = idxs[i + 1]
    ranges.append([x1, x2])
    return np.array(ranges)


def identifyLTThInsideRanges(x: np.ndarray, th, ranges):
    idxs = idxsUnderTH(x, th)
    idxs = groupClosePointsIntoRanges(idxs)
    return onlyIdxsInsideRanges(idxs, ranges)


def idxsUnderTH(x: np.ndarray, th):
    """Return a np.ndarray of indicies of the input signal `x` whose elements fall
    below `th`.
    """
    return np.where(x < th)[0]


def length(x: np.ndarray):
    return np.linalg.norm(x, axis=1)


def lowpass(x: np.ndarray, Wn, ftype='butter2'):
    if ftype == 'butter2':
        sos = signal.butter(2, Wn, 'low', output='sos')
        return signal.sosfiltfilt(sos, x, axis=0)
    
    else:
        return x


def mae(x1: np.ndarray, x2: np.ndarray):
    """Mean absolute error between `x1` and `x2`."""
    return np.mean(np.abs(x1 - x2))


def makeContinuousRange3dof(x: np.ndarray, fix_0=True, fix_1=True, fix_2=True, debug_file=None):
    """Runs `fixZeroCrossing()` for each column signal in the input ndarray `x`
    
    Returns the ndarray, with fixed zero crossings on each column signal individually.
    """
    return np.transpose([
        np.array(makeContinuousRange(x[:, 0].tolist(), debug_file=debug_file)[0]) if fix_0 else x[:, 0],
        np.array(makeContinuousRange(x[:, 1].tolist(), debug_file=debug_file)[0]) if fix_1 else x[:, 1],
        np.array(makeContinuousRange(x[:, 2].tolist(), debug_file=debug_file)[0]) if fix_2 else x[:, 2],
    ])


def maxIndex(x: np.ndarray, r=None):
    """Population max index with of input signal `x`"""
    if x.shape[0] == 0:
        return -1
    if r is None:
        return np.argmax(x)
    if r[0] == r[1]:
        return r[0]
    
    window = x[r[0]:r[1]]
    return r[0] + np.argmax(window)


def mse(x1: np.ndarray, x2: np.ndarray):
    """Mean sum error between `x1` and `x2`."""
    return np.mean((x1 - x2)**2)


def minIndex(x: np.ndarray, r=None):
    """Population min index with of input signal `x`"""
    if x.shape[0] == 0:
        return -1
    if r is None:
        return np.argmin(x)
    if r[0] == r[1]:
        return r[0]
    
    window = x[r[0]:r[1]]
    return r[0] + np.argmin(window)


def rmse(x1: np.ndarray, x2: np.ndarray):
    """Root mean sum error between `x1` and `x2`."""
    return np.sqrt(mse(x1, x2))


def zeroCrossingIdxs(x: np.ndarray) -> np.ndarray:
    xsign = np.sign(x)
    sign_changes = (np.roll(xsign, 1) - xsign) != 0
    return np.where(sign_changes > 0)[0]


def zeroCrossingIdxsGTThInsideRanges(x: np.ndarray, th, ranges) -> np.ndarray:
    sign_changes_r = zeroCrossingIdxs(x)
    large_diff_r = np.where(-np.diff(x) > th)[0]

    idxs = np.intersect1d(sign_changes_r, large_diff_r)
    return onlyIdxsInsideRanges(idxs, ranges)