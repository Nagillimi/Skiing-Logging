import math

def mean(x):
    return sum(x) / len(x)

def variance(x):
    '''Population variance
    `sum((xi - mean(x))**2) / len(x)`
    '''
    u = mean(x)
    return sum([(xi - u)**2 for xi in x]) / len(x)

def std(x):
    return math.sqrt(variance(x))

def length(ax, ay, az):
    return [math.sqrt(ax[i]**2 + ay[i]**2 + az[i]**2) for i in range(len(ax))]

def lowpass(x, fc, fs=100):
    delta_t = 1 / fs
    lpfi = x[0]
    lpf = []
    for xi in x: 
        lpfi += fc * (xi - lpfi) * delta_t
        lpf.append(lpfi)
    return lpf

def idxsUnderTH(x, th=200):
    return [x.index(xi) for xi in x if xi < th]