from jump import Jump
from signal_processing import length
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
    fig, _ax = plt.subplots(4, sharex=True, layout="constrained", figsize=(25, 15))
    _ax[0].plot(track.time, track.corrected_alt, label='Altitude')
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
    return fig


def plotAltGyr(track: Tile):
    plt.rc('lines', linewidth=1)
    fig, ax = plt.subplots(4, sharex=True, layout="constrained", figsize=(25, 15))
    ax[0].plot(track.time, track.corrected_alt, label='Altitude')
    ax[0].set_title('Tile Altitude', wrap=True)

    ax[1].plot(track.time, track.gx, label='Gx')
    ax[1].set_title('Tile Gyroscope X', wrap=True)

    ax[2].plot(track.time, track.gy, label='Gy')
    ax[2].set_title('Tile Gyroscope Y', wrap=True)

    ax[3].plot(track.time, track.gz, label='Gz')
    ax[3].set_title('Tile Gyroscope Z', wrap=True)

    plt.show()
    return fig


def plotAltMag(track: Tile):
    plt.rc('lines', linewidth=1)
    fig, ax = plt.subplots(4, sharex=True, layout="constrained", figsize=(25, 15))
    ax[0].plot(track.time, track.corrected_alt, label='Altitude')
    ax[0].set_title('Tile Altitude', wrap=True)

    ax[1].plot(track.time, track.mx, label='Mx')
    ax[1].set_title('Tile Magnetometer X', wrap=True)

    ax[2].plot(track.time, track.my, label='My')
    ax[2].set_title('Tile Magnetometer Y', wrap=True)

    ax[3].plot(track.time, track.mz, label='Mz')
    ax[3].set_title('Tile Magnetometer Z', wrap=True)

    plt.show()
    return fig


def plotTileRuns(runs: [Tile]):
    plt.rc('lines', linewidth=1)
    fig, ax = plt.subplots()
    for i in range(len(runs)): ax.plot(runs[i].time, runs[i].corrected_alt, label=['Tile Run', i])
    ax.set_title('Functional method for the Synchronized Tile vs. Stitched Tile (runs only from F6P timestamps, offset from A50)', wrap=True)
    
    plt.show()
    return fig


def plotJumpAnalysis(track: Tile, jump_idx: int):
    min_i = track.jumps[jump_idx].min_idx
    air_r = track.jumps[jump_idx].air_range
    landing_r = track.jumps[jump_idx].landing_range
    mg_raw = length(track.ax, track.ay, track.az)
    mg_filt = track.mG_lpf
    gyro = length(track.gx, track.gy, track.gz)

    # plot indices
    i1 = air_r[0]; i2 = landing_r[1]

    # convert min idx into ts for x axis
    min_t = track.time[min_i]

    plt.rc('lines', linewidth=1)
    fig, ax = plt.subplots(3, figsize=(8, 4))

    ax[0].plot(track.time[i1:i2], mg_filt[i1:i2])
    ax[0].plot(track.time[i1:i2], [Jump.mGThreshold() for _ in mg_filt[i1:i2]], 'k--')
    ax[0].axvspan(track.time[air_r[0]], track.time[air_r[1]], color='green', alpha=0.5)
    ax[0].axvline(x=min_t, ls=':', color='k')
    ax[0].axvspan(track.time[landing_r[0]], track.time[landing_r[1]], color='red', alpha=0.5)
    ax[0].set_title('Jump ')# + (jump_idx + 1) + ' Tile Filtered mG-force (& threshold)', wrap=True)

    ax[1].plot(track.time[i1:i2], mg_raw[i1:i2])
    ax[1].axvspan(track.time[air_r[0]], track.time[air_r[1]], color='green', alpha=0.5)
    ax[1].axvline(x=min_t, ls=':', color='k')
    ax[1].axvspan(track.time[landing_r[0]], track.time[landing_r[1]], color='red', alpha=0.5)
    ax[1].set_title('Jump ')# + (jump_idx + 1) + ' Tile Unfiltered mG-force', wrap=True)

    ax[2].plot(track.time[i1:i2], gyro[i1:i2])
    ax[2].axvspan(track.time[air_r[0]], track.time[air_r[1]], color='green', alpha=0.5)
    ax[2].axvline(x=min_t, ls=':', color='k')
    ax[2].axvspan(track.time[landing_r[0]], track.time[landing_r[1]], color='red', alpha=0.5)
    ax[2].set_title('Jump ')# + (jump_idx + 1) + ' Tile Unfiltered Gyroscope', wrap=True)
    
    plt.tight_layout()
    plt.show()
    return fig