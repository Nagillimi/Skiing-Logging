import numpy as np
from scipy import signal
from utilities.sig_proc import makeContinuousRange


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


def identifyRangesBelowTH(x: np.ndarray, th):
    idxs = idxsUnderTH(x, th)
    return groupClosePointsIntoRanges(idxs)


def idxsUnderTH(x: np.ndarray, th=200):
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


def makeContinuousRange3dof(x: np.ndarray, fix_0=True, fix_1=True, fix_2=True, print_out=False):
    """Runs `fixZeroCrossing()` for each column signal in the input ndarray `x`
    
    Returns the ndarray, with fixed zero crossings on each column signal individually.
    """
    return np.transpose([
        np.array(makeContinuousRange(x[:, 0].tolist(), print_out=print_out)[0]) if fix_0 else x[:, 0],
        np.array(makeContinuousRange(x[:, 1].tolist(), print_out=print_out)[0]) if fix_1 else x[:, 1],
        np.array(makeContinuousRange(x[:, 2].tolist(), print_out=print_out)[0]) if fix_2 else x[:, 2],
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