from jump import JUMP_THRESHOLD_MG
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


def plot3DofSignalWithAlt(t, a, x, y, z, signal="", r=[0, -1]):
    plt.rc('lines', linewidth=1)
    fig, ax = plt.subplots(4, sharex=True, layout="constrained", figsize=(25, 15))
    ax[0].plot(t[r[0]:r[1]], a[r[0]:r[1]])
    ax[0].set_title('Tile Altitude', wrap=True)

    ax[1].plot(t[r[0]:r[1]], x[r[0]:r[1]])
    ax[1].set_title('Tile ' + signal + ' X', wrap=True)

    ax[2].plot(t[r[0]:r[1]], y[r[0]:r[1]])
    ax[2].set_title('Tile ' + signal + ' Y', wrap=True)

    ax[3].plot(t[r[0]:r[1]], z[r[0]:r[1]])
    ax[3].set_title('Tile ' + signal + ' Z', wrap=True)

    plt.show()
    return fig


def plotAltAcc(track: Tile, r=[0, -1]):
    return plot3DofSignalWithAlt(
        track.time,
        track.alt_lpf,
        track.ax, track.ay, track.az,
        "Accelerometer",
        r=r
    )


def plotAltGyr(track: Tile, r=[0, -1]):
    return plot3DofSignalWithAlt(
        track.time,
        track.alt_lpf,
        track.ax, track.ay, track.az,
        "Gyroscope",
        r=r
    )


def plotAltMag(track: Tile, r=[0, -1]):
    return plot3DofSignalWithAlt(
        track.time,
        track.alt_lpf,
        track.ax, track.ay, track.az,
        "Mangnetometer",
        r=r
    )


def plotTileRuns(runs: [Tile]):
    plt.rc('lines', linewidth=1)
    fig, ax = plt.subplots()
    for i in range(len(runs)): ax.plot(runs[i].time, runs[i].alt_lpf, label=['Tile Run', i])
    ax.set_title('Functional method for the Synchronized Tile vs. Stitched Tile (runs only from F6P timestamps, offset from A50)', wrap=True)
    
    plt.show()
    return fig


def plotJumpAnalysis(tile: Tile, jump_idx: int, run_number=1):
    jump = tile.jumps[jump_idx]
    min_i = jump.min_idx
    air_r = jump.air_range
    landing_r = jump.landing_range
    mg_raw = tile.mG
    mg_filt = tile.mG_lpf
    gyro = tile.gyro_v

    # plot indices
    i1 = air_r[0]; i2 = landing_r[1]

    # convert min idx into ts for x axis
    min_t = tile.time[min_i]

    def markupWithJumpStages(ax):
        ax.axvspan(tile.time[air_r[0]], tile.time[air_r[1]], color='green', alpha=0.5)
        ax.axvline(x=min_t, ls=':', color='k')
        ax.axvspan(tile.time[landing_r[0]], tile.time[landing_r[1]], color='red', alpha=0.5)

    plt.rc('lines', linewidth=1)
    fig, ax = plt.subplots(3, figsize=(8, 6))

    ax[0].plot(tile.time[i1:i2], mg_filt[i1:i2])
    ax[0].plot(tile.time[i1:i2], [JUMP_THRESHOLD_MG for _ in mg_filt[i1:i2]], 'k--')
    markupWithJumpStages(ax[0])
    ax[0].set_title(f'{round(jump.confidence)}% | Run {run_number} Jump {jump_idx + 1} Tile Filtered mG-force (& threshold)', wrap=True)

    ax[1].plot(tile.time[i1:i2], mg_raw[i1:i2])
    markupWithJumpStages(ax[1])
    ax[1].set_title(f'{round(jump.confidence)}% | Run {run_number} Jump {jump_idx + 1}  Tile Unfiltered mG-force', wrap=True)

    ax[2].plot(tile.time[i1:i2], gyro[i1:i2])
    markupWithJumpStages(ax[2])
    ax[2].set_title(f'{round(jump.confidence)}% | Run {run_number} Jump {jump_idx + 1}  Tile Unfiltered Gyroscope', wrap=True)
    
    plt.tight_layout()
    plt.show()
    return fig


def plotAllJumpAnalyses(runs):
    for i, run in enumerate(runs):
        for j in range(len(run.jumps)):
            _ = plotJumpAnalysis(run, j, i)


def plotTileWithStillZones(tile: Tile, r=[0, -1]):
    def addStillZones(ax, t, ranges, r, _color='green'):
        for range in ranges:
            if tile.time[range[0]] < tile.time[r[0]] or tile.time[range[1]] > tile.time[r[1]]: 
                continue
            ax.axvspan(t[range[0]], t[range[1]], color=_color, alpha=0.25)

    fine_rs = [r for r in tile.static_registration.ranges if r is not None]
    coarse_rs = tile.static_registration.coarse_ranges
    t = tile.time[r[0]:r[1]]
    euler = tile.imu.euler[r[0]:r[1], :]

    plt.rc('lines', linewidth=1)
    fig, ax = plt.subplots(6, figsize=(15, 10))

    ax[0].plot(t, tile.alt_lpf[r[0]:r[1]])
    addStillZones(ax[0], tile.time, fine_rs, r)
    if coarse_rs is not None: addStillZones(ax[0], tile.time, coarse_rs, r, 'red')
    ax[0].set_title('All Tile Altitude with Still Zones', wrap=True)

    ax[1].plot(t, euler[:, 0], label='9dof')
    addStillZones(ax[1], tile.time, fine_rs, r)
    if coarse_rs is not None: addStillZones(ax[1], tile.time, coarse_rs, r, 'red')
    ax[1].set_title('All Tile Roll with Still Zones', wrap=True)
    ax[1].legend()

    ax[2].plot(t, euler[:, 1], label='9dof')
    addStillZones(ax[2], tile.time, fine_rs, r)
    if coarse_rs is not None: addStillZones(ax[2], tile.time, coarse_rs, r, 'red')
    ax[2].set_title('All Tile Pitch with Still Zones', wrap=True)
    ax[2].legend()

    ax[3].plot(t, euler[:, 2], label='9dof')
    addStillZones(ax[3], tile.time, fine_rs, r)
    if coarse_rs is not None: addStillZones(ax[3], tile.time, coarse_rs, r, 'red')
    ax[3].set_title('All Tile Yaw with Still Zones', wrap=True)
    ax[3].legend()

    ax[4].plot(t, tile.mG_lpf[r[0]:r[1]])
    addStillZones(ax[4], tile.time, fine_rs, r)
    if coarse_rs is not None: addStillZones(ax[4], tile.time, coarse_rs, r, 'red')
    ax[4].set_title('All Tile Filtered mG-forces with Still Zones', wrap=True)

    ax[5].plot(t, tile.mG[r[0]:r[1]])
    addStillZones(ax[5], tile.time, fine_rs, r)
    if coarse_rs is not None: addStillZones(ax[5], tile.time, coarse_rs, r, 'red')
    ax[5].set_title('All Tile Unfiltered mG-forces with Still Zones', wrap=True)

    plt.tight_layout()
    plt.show()
    return fig


def plotAllTileRegistationZones(tile: Tile, r=[0, -1]):
    coarse_rs = tile.static_registration.coarse_ranges

    _ = plotTileWithStillZones(tile, r=r)
    brackets = [[r[0]-3000, r[1]+3000] for r in coarse_rs]
    _ = [plotTileWithStillZones(tile, r=bracket) for bracket in brackets]