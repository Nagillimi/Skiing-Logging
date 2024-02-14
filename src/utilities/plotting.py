import numpy as np
import matplotlib.pyplot as plt
from constants.jump_th import JUMP_THRESHOLD_MG
from domain.devices.track import Track
from models.tile import Tile
from utilities.quat import eulerToQuat, quatRot, quatToEuler
from utilities.sig_proc_np import deriv

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


def plotTileRuns(runs: list[Tile]):
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
    fig, ax = plt.subplots(5, figsize=(10, 6))

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

    ax[4].plot(t, tile.mG[r[0]:r[1]])
    addStillZones(ax[4], tile.time, fine_rs, r)
    if coarse_rs is not None: addStillZones(ax[4], tile.time, coarse_rs, r, 'red')
    ax[4].set_title('All Tile Unfiltered mG-forces with Still Zones', wrap=True)

    plt.tight_layout()
    plt.show()
    return fig


def plotAllTileRegistationZones(tile: Tile, r=[0, -1]):
    coarse_rs = tile.static_registration.coarse_ranges

    _ = plotTileWithStillZones(tile, r=r)
    brackets = [[r[0]-3000, r[1]+3000] for r in coarse_rs]
    _ = [plotTileWithStillZones(tile, r=bracket) for bracket in brackets]


def plotEulerAnalysis(tile: Tile, r=[0, -1]):
    def addStillZones(ax, t, ranges, r, _color='green'):
        for range in ranges:
            if tile.time[range[0]] < tile.time[r[0]] or tile.time[range[1]] > tile.time[r[1]]: 
                continue
            ax.axvspan(t[range[0]], t[range[1]], color=_color, alpha=0.25)

    def addHorizontalLines(ax):
        ax.axhline(y=0, color='k', linestyle='--')
        ax.axhline(y=90, color='k', linestyle='--')
        ax.axhline(y=180, color='k', linestyle='--')
        ax.axhline(y=-90, color='k', linestyle='--')
        ax.axhline(y=-180, color='k', linestyle='--')

    fine_rs = [r for r in tile.static_registration.ranges if r is not None]
    coarse_rs = tile.static_registration.coarse_ranges
    t = tile.time[r[0]:r[1]]


    boot_quat = tile.boot_quat[r[0]:r[1], :]
    boot_quat_euler = np.apply_along_axis(quatToEuler, 1, boot_quat)
    # boot_quat_euler = makeContinuousRange3dof(boot_quat_euler, fix_0=True, fix_1=True, fix_2=True)

    sensor_quat = tile.imu.quat[r[0]:r[1], :]
    sensor_euler = np.apply_along_axis(quatToEuler, 1, sensor_quat)
    # sensor_euler = makeContinuousRange3dof(sensor_euler, fix_0=True, fix_1=True, fix_2=True)

    boot_rotated_euler = tile.boot_rotated_euler[r[0]:r[1], :]
    # boot_rotated_euler = makeContinuousRange3dof(boot_rotated_euler, fix_0=True, fix_1=True, fix_2=True)

    boot_rotM_euler = tile.boot_rotM_euler[r[0]:r[1], :]
    # boot_rotM_euler = makeContinuousRange3dof(boot_rotM_euler, fix_0=True, fix_1=True, fix_2=True)

    plt.rc('lines', linewidth=1)
    fig, ax = plt.subplots(4, figsize=(15, 10))

    ax[0].plot(t, tile.alt_lpf[r[0]:r[1]])
    addStillZones(ax[0], tile.time, fine_rs, r)
    addStillZones(ax[0], tile.time, coarse_rs, r, 'red')
    ax[0].set_title('All Tile Altitude with Still Zones', wrap=True)

    ax[1].plot(t, sensor_euler[:, 0], label='sensor')
    ax[1].plot(t, boot_quat_euler[:, 0], label='boot_quat_euler')
    ax[1].plot(t, boot_rotated_euler[:, 0], label='boot_rotated_euler')
    ax[1].plot(t, boot_rotM_euler[:, 0], label='boot_rotM_euler')
    addStillZones(ax[1], tile.time, fine_rs, r)
    addStillZones(ax[1], tile.time, coarse_rs, r, 'red')
    addHorizontalLines(ax[1])
    ax[1].set_title('All Tile Roll with Still Zones', wrap=True)
    ax[1].legend()

    ax[2].plot(t, sensor_euler[:, 1], label='sensor')
    ax[2].plot(t, boot_quat_euler[:, 1], label='boot_quat_euler')
    ax[2].plot(t, boot_rotated_euler[:, 1], label='boot_rotated_euler')
    ax[2].plot(t, boot_rotM_euler[:, 1], label='boot_rotM_euler')
    addStillZones(ax[2], tile.time, fine_rs, r)
    addStillZones(ax[2], tile.time, coarse_rs, r, 'red')
    addHorizontalLines(ax[2])
    ax[2].set_title('All Tile Pitch with Still Zones', wrap=True)
    ax[2].legend()

    ax[3].plot(t, sensor_euler[:, 2], label='sensor')
    ax[3].plot(t, boot_quat_euler[:, 2], label='boot_quat_euler')
    ax[3].plot(t, boot_rotated_euler[:, 2], label='boot_rotated_euler')
    ax[3].plot(t, boot_rotM_euler[:, 2], label='boot_rotM_euler')
    addStillZones(ax[3], tile.time, fine_rs, r)
    addStillZones(ax[3], tile.time, coarse_rs, r, 'red')
    addHorizontalLines(ax[3])
    ax[3].set_title('All Tile Yaw with Still Zones', wrap=True)
    ax[3].legend()

    plt.tight_layout()
    plt.show()
    return fig


def plotAllTileEulerAnalyses(tile: Tile, r=[0, -1]):
    _ = plotEulerAnalysis(tile, r=r)
    brackets = [[r[1], r[1]+10000] for r in tile.static_registration.ranges]
    if len(brackets) > 0:
        for i, bracket in enumerate(brackets):
            print('Orientation offset in boot frame:', quatToEuler(tile.q_offset_bf[i + 1]))
            _ = plotEulerAnalysis(tile, r=bracket)


def plotSensorBootEuler(tile: Tile, r=[0, -1]):
    def addStillZones(ax, t, ranges, r, _color='green'):
        for range in ranges:
            if tile.time[range[0]] < tile.time[r[0]] or tile.time[range[1]] > tile.time[r[1]]: 
                continue
            ax.axvspan(t[range[0]], t[range[1]], color=_color, alpha=0.25)

    def addHorizontalLines(ax):
        ax.axhline(y=0, color='k', linestyle='--')
        ax.axhline(y=90, color='k', linestyle='--')
        ax.axhline(y=180, color='k', linestyle='--')
        ax.axhline(y=-90, color='k', linestyle='--')
        ax.axhline(y=-180, color='k', linestyle='--')

    fine_rs = [r for r in tile.static_registration.ranges if r is not None]
    coarse_rs = tile.static_registration.coarse_ranges
    t = tile.time[r[0]:r[1]]


    boot_quat = tile.boot_quat[r[0]:r[1], :]
    boot_quat_euler = np.apply_along_axis(quatToEuler, 1, boot_quat)
    # boot_quat_euler = makeContinuousRange3dof(boot_quat_euler, fix_0=True, fix_1=True, fix_2=True)

    sensor_quat = tile.imu.quat[r[0]:r[1], :]
    sensor_euler = np.apply_along_axis(quatToEuler, 1, sensor_quat)
    # sensor_euler = makeContinuousRange3dof(sensor_euler, fix_0=True, fix_1=True, fix_2=True)

    plt.rc('lines', linewidth=1)
    fig, ax = plt.subplots(4, figsize=(15, 10))

    ax[0].plot(t, tile.alt_lpf[r[0]:r[1]])
    addStillZones(ax[0], tile.time, fine_rs, r)
    addStillZones(ax[0], tile.time, coarse_rs, r, 'red')
    ax[0].set_title('All Tile Altitude with Still Zones', wrap=True)

    ax[1].plot(t, sensor_euler[:, 0], label='sensor')
    ax[1].plot(t, boot_quat_euler[:, 0], label='boot')
    addStillZones(ax[1], tile.time, fine_rs, r)
    addStillZones(ax[1], tile.time, coarse_rs, r, 'red')
    addHorizontalLines(ax[1])
    ax[1].set_title('All Tile Roll with Still Zones', wrap=True)
    ax[1].legend()

    ax[2].plot(t, sensor_euler[:, 1], label='sensor')
    ax[2].plot(t, boot_quat_euler[:, 1], label='boot')
    addStillZones(ax[2], tile.time, fine_rs, r)
    addStillZones(ax[2], tile.time, coarse_rs, r, 'red')
    addHorizontalLines(ax[2])
    ax[2].set_title('All Tile Pitch with Still Zones', wrap=True)
    ax[2].legend()

    ax[3].plot(t, sensor_euler[:, 2], label='sensor')
    ax[3].plot(t, boot_quat_euler[:, 2], label='boot')
    addStillZones(ax[3], tile.time, fine_rs, r)
    addStillZones(ax[3], tile.time, coarse_rs, r, 'red')
    addHorizontalLines(ax[3])
    ax[3].set_title('All Tile Yaw with Still Zones', wrap=True)
    ax[3].legend()

    plt.tight_layout()
    plt.show()
    return fig


def plotAllSensorBootEuler(tile: Tile, r=[0, -1]):
    _ = plotSensorBootEuler(tile, r=r)
    brackets = [[r[1], r[1]+10000] for r in tile.static_registration.ranges]
    if len(brackets) > 0:
        for bracket in brackets:
            _ = plotSensorBootEuler(tile, r=bracket)


def plotTurnAnalysis(tile: Tile, rrs=None, r=[0, -1]):
    def addVerticalLines(ax, t, override_rrs=None, _color='k', _label=''):
        for i, rr in enumerate(rrs if override_rrs is None else override_rrs):
            if t[rr] < t[r[0]] or t[rr] > t[r[1]]: 
                continue
            ax.axvline(
                t[rr],
                color=_color,
                linestyle='--' if override_rrs is None else '-',
                label=_label if i == 0 else None
            )

    def addRunZones(ax, t):
        for i in range(tile.downhill_idxs.shape[0]):
            if t[tile.downhill_idxs[i, 0]] > t[r[0]] and t[tile.downhill_idxs[i, 1]] < t[r[1]]: 
                ax.axvspan(t[tile.downhill_idxs[i, 0]], t[tile.downhill_idxs[i, 1]], color='g', alpha=0.25)

    t = tile.time[r[0]:r[1]]
    euler = np.apply_along_axis(quatToEuler, 1, tile.boot_quat[r[0]:r[1], :])

    highG_idxs = [turn.highG_idx for turn in tile.turns]
    baseline_idxs = [turn.baseline_idx for turn in tile.turns]
    max_roll_idxs = [turn.max_roll_idx for turn in tile.turns]
    min_dF_dt_idxs = [turn.min_dF_dt_idx for turn in tile.turns]

    plt.rc('lines', linewidth=1)
    fig, ax = plt.subplots(8, figsize=(18, 18))

    ax[0].plot(t, tile.alt_lpf[r[0]:r[1]])
    ax[0].set_title('Tile (lpf) Altitude', wrap=True)
    if rrs is not None:
        addVerticalLines(ax[0], tile.time)
    else:
        addVerticalLines(ax[0], tile.time, highG_idxs, 'r', 'high G')
        addVerticalLines(ax[0], tile.time, baseline_idxs, 'b', 'baseline')
        addVerticalLines(ax[0], tile.time, max_roll_idxs, 'g', 'max roll')
        addVerticalLines(ax[0], tile.time, min_dF_dt_idxs, 'y', 'min dF/ft')
    addRunZones(ax[0], tile.time)
    ax[0].legend()

    ax[1].plot(t, euler[:, 0])
    ax[1].set_title('Boot Roll (Edge angle)', wrap=True)
    ax[1].axhline(0, color='k', linestyle='--')
    if rrs is not None:
        addVerticalLines(ax[1], tile.time)
    else:
        addVerticalLines(ax[1], tile.time, highG_idxs, 'r', 'high G')
        addVerticalLines(ax[1], tile.time, baseline_idxs, 'b', 'baseline')
        addVerticalLines(ax[1], tile.time, max_roll_idxs, 'g', 'max roll')
        addVerticalLines(ax[1], tile.time, min_dF_dt_idxs, 'y', 'min dF/ft')
    addRunZones(ax[1], tile.time)
    ax[1].legend()

    ax[2].plot(t, deriv(euler[:, 0], 0.01))
    ax[2].set_title('Boot Roll (Edge angle) 1st Deriv.', wrap=True)
    ax[2].axhline(0, color='k', linestyle='--')
    if rrs is not None:
        addVerticalLines(ax[2], tile.time)
    else:
        addVerticalLines(ax[2], tile.time, highG_idxs, 'r', 'high G')
        addVerticalLines(ax[2], tile.time, baseline_idxs, 'b', 'baseline')
        addVerticalLines(ax[2], tile.time, max_roll_idxs, 'g', 'max roll')
        addVerticalLines(ax[2], tile.time, min_dF_dt_idxs, 'y', 'min dF/ft')
    addRunZones(ax[2], tile.time)
    ax[2].legend()

    ax[3].plot(t, euler[:, 1])
    ax[3].set_title('Boot Pitch (Flex angle)', wrap=True)
    ax[3].axhline(0, color='k', linestyle='--')
    if rrs is not None:
        addVerticalLines(ax[3], tile.time)
    else:
        addVerticalLines(ax[3], tile.time, highG_idxs, 'r', 'high G')
        addVerticalLines(ax[3], tile.time, baseline_idxs, 'b', 'baseline')
        addVerticalLines(ax[3], tile.time, max_roll_idxs, 'g', 'max roll')
        addVerticalLines(ax[3], tile.time, min_dF_dt_idxs, 'y', 'min dF/ft')
    addRunZones(ax[3], tile.time)
    ax[3].legend()

    ax[4].plot(t, euler[:, 2])
    ax[4].set_title('Boot Yaw (Heading)', wrap=True)
    if rrs is not None:
        addVerticalLines(ax[4], tile.time)
    else:
        addVerticalLines(ax[4], tile.time, highG_idxs, 'r', 'high G')
        addVerticalLines(ax[4], tile.time, baseline_idxs, 'b', 'baseline')
        addVerticalLines(ax[4], tile.time, max_roll_idxs, 'g', 'max roll')
        addVerticalLines(ax[4], tile.time, min_dF_dt_idxs, 'y', 'min dF/ft')
    addRunZones(ax[4], tile.time)
    ax[4].legend()

    ax[5].plot(t, tile.g_force.mG_lpf[r[0]:r[1]])
    ax[5].set_title('Tile Filtered mG-forces', wrap=True)
    if rrs is not None:
        addVerticalLines(ax[5], tile.time)
    else:
        addVerticalLines(ax[5], tile.time, highG_idxs, 'r', 'high G')
        addVerticalLines(ax[5], tile.time, baseline_idxs, 'b', 'baseline')
        addVerticalLines(ax[5], tile.time, max_roll_idxs, 'g', 'max roll')
        addVerticalLines(ax[5], tile.time, min_dF_dt_idxs, 'y', 'min dF/ft')
    addRunZones(ax[5], tile.time)
    ax[5].legend()

    ax[6].plot(t, tile.g_force.d_mG_lpf_dt[r[0]:r[1]])
    ax[6].set_title('Tile Filtered mG-forces 1st Deriv.', wrap=True)
    ax[6].axhline(0, color='k', linestyle='--')
    if rrs is not None:
        addVerticalLines(ax[6], tile.time)
    else:
        addVerticalLines(ax[6], tile.time, highG_idxs, 'r', 'high G')
        addVerticalLines(ax[6], tile.time, baseline_idxs, 'b', 'baseline')
        addVerticalLines(ax[6], tile.time, max_roll_idxs, 'g', 'max roll')
        addVerticalLines(ax[6], tile.time, min_dF_dt_idxs, 'y', 'min dF/ft')
    addRunZones(ax[6], tile.time)
    ax[6].legend()

    ax[7].plot(t, tile.g_force.d2_mG_lpf_dt2[r[0]:r[1]])
    ax[7].set_title('Tile Filtered mG-forces 2nd Deriv.', wrap=True)
    ax[7].axhline(0, color='k', linestyle='--')
    if rrs is not None:
        addVerticalLines(ax[7], tile.time)
    else:
        addVerticalLines(ax[7], tile.time, highG_idxs, 'r', 'high G')
        addVerticalLines(ax[7], tile.time, baseline_idxs, 'b', 'baseline')
        addVerticalLines(ax[7], tile.time, max_roll_idxs, 'g', 'max roll')
        addVerticalLines(ax[7], tile.time, min_dF_dt_idxs, 'y', 'min dF/ft')
    addRunZones(ax[7], tile.time)
    ax[7].legend()

    plt.tight_layout()
    plt.show()
    return fig


def plotAllTurnAnalyses(tile: Tile, rrs=None, r=[0, -1]):
    _ = plotTurnAnalysis(tile, rrs=rrs, r=r)
    brackets = [[r[1], r[1]+12000] for r in tile.static_registration.ranges]
    if len(brackets) > 0:
        for bracket in brackets:
            _ = plotTurnAnalysis(tile, rrs=rrs, r=bracket)


def plotRunGeographyAnalysis(tile: Tile, r=[0, -1]):
    t = tile.time[r[0]:r[1]]
    boot_euler = np.apply_along_axis(quatToEuler, 1, tile.boot_quat[r[0]:r[1], :])
    lbs = [el.idx for el in tile.geography.lift_bottoms]
    lps = [el.idx for el in tile.geography.lift_peaks]
    rps = [el.idx for el in tile.geography.run_peaks]
    rbs = [el.idx for el in tile.geography.run_bottoms]

    def addKeyGeographicalPts(ax, t):
        for lb in lbs:
            if t[lb] > t[r[0]] and t[lb] < t[r[1]]: 
                ax.axvline(t[lb], color='k', linestyle='--')
        for lp in lps:
            if t[lp] > t[r[0]] and t[lp] < t[r[1]]: 
                ax.axvline(t[lp], color='k', linestyle='--')
        for rp in rps:
            if t[rp] > t[r[0]] and t[rp] < t[r[1]]: 
                ax.axvline(t[rp], color='g', linestyle='--')
        for rb in rbs:
            if t[rb] > t[r[0]] and t[rb] < t[r[1]]: 
                ax.axvline(t[rb], color='r', linestyle='--')

    def addKeyGeographicalZones(ax, t):
        for i in range(tile.downhill_idxs.shape[0]):
            if t[tile.downhill_idxs[i, 0]] > t[r[0]] and t[tile.downhill_idxs[i, 1]] < t[r[1]]: 
                ax.axvspan(t[tile.downhill_idxs[i, 0]], t[tile.downhill_idxs[i, 1]], color='g', alpha=0.25)
        for i in range(tile.lift_idxs.shape[0]):
            if t[tile.lift_idxs[i, 0]] > t[r[0]] and t[tile.lift_idxs[i, 1]] < t[r[1]]: 
                ax.axvspan(t[tile.lift_idxs[i, 0]], t[tile.lift_idxs[i, 1]], color='r', alpha=0.25)
        for i in range(tile.peak_idxs.shape[0]):
            if t[tile.peak_idxs[i, 0]] > t[r[0]] and t[tile.peak_idxs[i, 1]] < t[r[1]]: 
                ax.axvspan(t[tile.peak_idxs[i, 0]], t[tile.peak_idxs[i, 1]], color='y', alpha=0.25)

    plt.rc('lines', linewidth=1)
    fig, ax = plt.subplots(5, figsize=(15, 11))

    ax[0].plot(t, tile.alt_lpf[r[0]:r[1]])
    addKeyGeographicalPts(ax[0], tile.time)
    addKeyGeographicalZones(ax[0], tile.time)
    ax[0].set_title('Tile Altitude with Still Zones', wrap=True)

    ax[1].plot(t, boot_euler[:, 0])
    addKeyGeographicalPts(ax[1], tile.time)
    addKeyGeographicalZones(ax[1], tile.time)
    ax[1].set_title('Tile Roll with Still Zones', wrap=True)

    ax[2].plot(t, boot_euler[:, 1])
    addKeyGeographicalPts(ax[2], tile.time)
    addKeyGeographicalZones(ax[2], tile.time)
    ax[2].set_title('Tile Pitch with Still Zones', wrap=True)

    ax[3].plot(t, boot_euler[:, 2])
    addKeyGeographicalPts(ax[3], tile.time)
    addKeyGeographicalZones(ax[3], tile.time)
    ax[3].set_title('Tile Yaw with Still Zones', wrap=True)

    ax[4].plot(t, tile.mG_lpf[r[0]:r[1]])
    addKeyGeographicalPts(ax[4], tile.time)
    addKeyGeographicalZones(ax[4], tile.time)
    ax[4].set_title('Tile Filtered mG Forces with Still Zones', wrap=True)

    plt.tight_layout()
    plt.show()
    return fig
