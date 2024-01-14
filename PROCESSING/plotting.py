from track import Track
from tile import Tile
import matplotlib.pyplot as plt

def plot_a50_f6p(a: Track, f: Track):
    plt.rc('lines', linewidth=1)
    fig, axs = plt.subplots(2, 3, sharex=True, layout="constrained")

    axs[0, 0].plot(a.time, a.dist, label='A50')
    axs[0, 0].plot(f.time, f.dist, label='F6P')
    axs[0, 0].set_title("Distance [m]")

    
    axs[0, 1].plot(a.time, a.vel, label='A50')
    axs[0, 1].plot(f.time, f.vel, label='F6P')
    axs[0, 1].set_title("Velocity [m/s]")

    
    axs[0, 2].plot(a.time, a.alt, label='A50')
    axs[0, 2].plot(f.time, f.alt, label='F6P')
    axs[0, 2].set_title("Altitude [m]")

    
    axs[1, 0].plot(a.time, a.lat, label='A50')
    axs[1, 0].plot(f.time, f.lat, label='F6P')
    axs[1, 0].set_title("Latitude [°]")

    
    axs[1, 1].plot(a.time, a.long, label='A50')
    axs[1, 1].plot(f.time, f.long, label='F6P')
    axs[1, 1].set_title("Longitude [°]")

    axs[0, 0].legend()
    plt.show()
    return fig

def plotAltAcc(track: Tile, ax=None, ay=None, az=None):
    plt.rc('lines', linewidth=1)
    _, _ax = plt.subplots(4, sharex=True, layout="constrained", figsize=(25, 15))
    _ax[0].plot(track.time, track.alt, label='Altitude')
    _ax[0].set_title('Tile Altitude', wrap=True)

    if ax is None: _ax[1].plot(track.time, track.ax, label='Ax')
    else: _ax[1].plot(track.time, ax, label='Ax')
    _ax[1].set_title('Tile Accelerometer X', wrap=True)

    if ay is None: _ax[2].plot(track.time, track.ay, label='Ay')
    else: _ax[2].plot(track.time, ay, label='Ay')
    _ax[2].set_title('Tile Accelerometer Y', wrap=True)

    if az is None: _ax[3].plot(track.time, track.az, label='Az')
    else: _ax[3].plot(track.time, az, label='Az')
    _ax[3].set_title('Tile Accelerometer Z', wrap=True)

    plt.show()

def plotAltGyr(track: Tile):
    plt.rc('lines', linewidth=1)
    _, ax = plt.subplots(4, sharex=True, layout="constrained", figsize=(25, 15))
    ax[0].plot(track.time, track.alt, label='Altitude')
    ax[0].set_title('Tile Altitude', wrap=True)

    ax[1].plot(track.time, track.gx, label='Gx')
    ax[1].set_title('Tile Gyroscope X', wrap=True)

    ax[2].plot(track.time, track.gy, label='Gy')
    ax[2].set_title('Tile Gyroscope Y', wrap=True)

    ax[3].plot(track.time, track.gz, label='Gz')
    ax[3].set_title('Tile Gyroscope Z', wrap=True)

    plt.show()

def plotAltMag(track: Tile):
    plt.rc('lines', linewidth=1)
    _, ax = plt.subplots(4, sharex=True, layout="constrained", figsize=(25, 15))
    ax[0].plot(track.time, track.alt, label='Altitude')
    ax[0].set_title('Tile Altitude', wrap=True)

    ax[1].plot(track.time, track.mx, label='Mx')
    ax[1].set_title('Tile Magnetometer X', wrap=True)

    ax[2].plot(track.time, track.my, label='My')
    ax[2].set_title('Tile Magnetometer Y', wrap=True)

    ax[3].plot(track.time, track.mz, label='Mz')
    ax[3].set_title('Tile Magnetometer Z', wrap=True)

    plt.show()