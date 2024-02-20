import os
import numpy as np
from constants.jump_th import JUMP_THRESHOLD_MG
from constants.turn_th import D_MG_LPF_DT_TH
from models.tile import Tile
from models.jump import Jump
from models.turn import Turn
from utilities.quat import quatToEuler
from utilities.sig_proc import mean, std
from utilities.sig_proc_np import maxIndex, minIndex


JUMP_HEADER = 'mG_th,'\
    + 'lowG_range_1,lowG_range_2,lowG_range,'\
    + 'min_mG_lpf[lowG_range],max_mG_lpf[lowG_range],mean_mG_lpf[lowG_range],std_mG_lpf[lowG_range],'\
    + 'min_mG[lowG_range],max_mG[lowG_range],mean_mG[lowG_range],std_mG[lowG_range],'\
    + 'min_gyro[lowG_range],max_gyro[lowG_range],mean_gyro[lowG_range],std_gyro[lowG_range],'\
    + 'min_idx,mG_lpf[min_idx],mG[min_idx],gyro[min_idx],'\
    + 'air_range_1,air_range_2,air_range,'\
    + 'min_mG_lpf[air_range],max_mG_lpf[air_range],mean_mG_lpf[air_range],std_mG_lpf[air_range],'\
    + 'min_mG[air_range],max_mG[air_range],mean_mG[air_range],std_mG[air_range],'\
    + 'min_gyro[air_range],max_gyro[air_range],mean_gyro[air_range],std_gyro[air_range],'\
    + 'liftoff_idx,mG_lpf[liftoff_idx],mG[liftoff_idx],gyro[liftoff_idx],'\
    + 'touch_idx,mG_lpf[touch_idx],mG[touch_idx],gyro[touch_idx],'\
    + 'landing_range_1,landing_range_2,landing_range,'\
    + 'min_mG_lpf[landing_range],max_mG_lpf[landing_range],mean_mG_lpf[landing_range],std_mG_lpf[landing_range],'\
    + 'min_mG[landing_range],max_mG[landing_range],mean_mG[landing_range],std_mG[landing_range],'\
    + 'min_gyro[landing_range],max_gyro[landing_range],mean_gyro[landing_range],std_gyro[landing_range],'\
    + 'full_jump_range,'\
    + 'min_mG_lpf[full_jump_range],max_mG_lpf[full_jump_range],mean_mG_lpf[full_jump_range],std_mG_lpf[full_jump_range],'\
    + 'min_mG[full_jump_range],max_mG[full_jump_range],mean_mG[full_jump_range],std_mG[full_jump_range],'\
    + 'min_gyro[full_jump_range],max_gyro[full_jump_range],mean_gyro[full_jump_range],std_gyro[full_jump_range],'\
    + 'impulse_idx,mG_lpf[impulse_idx],mG[impulse_idx],gyro[impulse_idx],'\
    + 'distance,tests_passed,total_tests,confidence,run_sample_count,'\
    + 'min_mG_lpf[full_range],max_mG_lpf[full_range],mean_mG_lpf[full_range],std_mG_lpf[full_range],'\
    + 'min_mG[full_range],max_mG[full_range],mean_mG[full_range],std_mG[full_range],'\
    + 'min_gyro[full_range],max_gyro[full_range],mean_gyro[full_range],std_gyro[full_range]'\
    + '\n'
"""Header for confirming jump identification. Designed for ML."""


SENSOR_BOOT_HEADER = 'time [s],alt_lpf [m],sensor_roll,sensor_pitch,sensor_yaw,'\
    + 'offset_roll,offset_pitch,offset_yaw,'\
    + 'boot_roll,boot_pitch,boot_yaw,'\
    + 'min_mG_lpf[turn_range],max_mG_lpf[turn_range],mean_mG_lpf[turn_range],std_mG_lpf[turn_range],'\
    + '\n'
"""Header for the sensor boot comparison datafile."""


TURN_HEADER = 'd_mG_lpf_dt_th,'\
    + 'side,highG_idx,'\
    + 'baseline_idx_1,baseline_idx_2,baseline_idx_3,baseline_idx_4,baseline_idx_5,'\
    + 'peak_roll_idx,past_peak_roll_idx,'\
    + 'turn_range_1,turn_range_2,turn_range,'\
    + 'baseline_range_1,baseline_range_2,baseline_range,'\
    + 'min_radius_range_1,min_radius_range_2,min_radius_range,'\
    + 'mG_lpf[highG_idx],d_boot_roll_dt[highG_idx],offset_abs_roll[highG_idx],'\
    + 'min_mG_lpf[turn_range],max_mG_lpf[turn_range],mean_mG_lpf[turn_range],std_mG_lpf[turn_range],'\
    + 'min_mG_lpf[baseline_range],max_mG_lpf[baseline_range],mean_mG_lpf[baseline_range],std_mG_lpf[baseline_range],'\
    + 'min_mG_lpf[min_radius_range_range],max_mG_lpf[min_radius_range_range],mean_mG_lpf[min_radius_range_range],std_mG_lpf[min_radius_range_range],'\
    + 'min_offset_abs_roll[turn_range],max_offset_abs_roll[turn_range],mean_offset_abs_roll[turn_range],std_offset_abs_roll[turn_range],'\
    + 'min_offset_abs_roll[baseline_range],max_offset_abs_roll[baseline_range],mean_offset_abs_roll[baseline_range],std_offset_abs_roll[baseline_range],'\
    + 'min_offset_abs_roll[min_radius_range_range],max_offset_abs_roll[min_radius_range_range],mean_offset_abs_roll[min_radius_range_range],std_offset_abs_roll[min_radius_range_range],'\
    + 'min_d_roll_dt[turn_range],max_d_roll_dt[turn_range],mean_d_roll_dt[turn_range],std_d_roll_dt[turn_range],'\
    + 'min_d_roll_dt[baseline_range],max_d_roll_dt[baseline_range],mean_d_roll_dt[baseline_range],std_d_roll_dt[baseline_range],'\
    + 'min_d_roll_dt[min_radius_range_range],max_d_roll_dt[min_radius_range_range],mean_d_roll_dt[min_radius_range_range],std_d_roll_dt[min_radius_range_range],'\
    + 'min_alt_lpf[turn_range],max_alt_lpf[turn_range],mean_alt_lpf[turn_range],std_alt_lpf[turn_range],'\
    + 'min_alt_lpf[baseline_range],max_alt_lpf[baseline_range],mean_alt_lpf[baseline_range],std_alt_lpf[baseline_range],'\
    + 'min_alt_lpf[min_radius_range_range],max_alt_lpf[min_radius_range_range],mean_alt_lpf[min_radius_range_range],std_d_roll_dt[min_radius_range_range],'\
    + 'carving_angle_1,carving_angle_2, carving_angle_3,carving_angle_4,carving_angle_5,'\
    + 'max_idx[mG_lpf[turn_range]],'\
    + 'max_idx[offset_abs_roll[turn_range]],'\
    + 'max_idx[d_roll_dt[turn_range]],'\
    + 'min_idx[mG_lpf[turn_range]],'\
    + 'min_idx[offset_abs_roll[turn_range]],'\
    + 'min_idx[d_roll_dt[turn_range]]'\
    + '\n'
"""Header for confirming turn identification. Designed for ML."""


def createDataFile(name='data.csv', subdir='', header=''):
    """Creates a generic data file inside the `logs/` dir.
    
    Checks that the logs dir exists, if not creates it.

    Checks to see if the logfile already exists, then overwrites it.
    """
    # ensure the logs dir exists, if not create it
    if not os.path.exists(os.path.join(os.getcwd().split('src')[0], 'logs')):
        os.mkdir(os.path.join(os.getcwd().split('src')[0], 'logs'))

    # if you want a subdir, ensure the subdir exists, if not create it
    if subdir and not os.path.exists(os.path.join(os.getcwd().split('src')[0], f'logs/{subdir}')):
        os.mkdir(os.path.join(os.getcwd().split('src')[0], f'logs/{subdir}'))
    
    # delete previous file with matching name if it exists (for good measure)
    if os.path.exists(os.path.join(os.getcwd().split('src')[0], (f'logs/{subdir}/{name}' if subdir else f'logs/{name}'))):
        os.remove(os.path.join(os.getcwd().split('src')[0], (f'logs/{subdir}/{name}' if subdir else f'logs/{name}')))

    file = open(os.path.join(os.getcwd().split('src')[0], (f'logs/{subdir}/{name}' if subdir else f'logs/{name}')), "w")
    file.write(header)
    return file


def createJumpDataFile(name):
    """Creates a specific logfile for jump data."""
    return createDataFile(name=name, subdir='jump', header=JUMP_HEADER)


def createSensorBootDataFile(name):
    """Creates a specific logfile for sensor boot frame data."""
    return createDataFile(name=name, subdir='sensor_boot', header=SENSOR_BOOT_HEADER)


def createTurnDataFile(name):
    """Creates a specific logfile for sensor boot frame data."""
    return createDataFile(name=name, subdir='turn', header=TURN_HEADER)


def constructJumpLine(jump: Jump):
    """Constructs the (lengthy) data row based on the jump."""
    line = f'{JUMP_THRESHOLD_MG},'
    line += f'{jump.lowG_range[0]},'
    line += f'{jump.lowG_range[1]},'
    line += f'{jump.lowG_range[1] - jump.lowG_range[0]},'
    line += f'{jump.mG_lpf[jump.lowG_range[0]] if jump.lowG_range[0] == jump.lowG_range[1] else min(jump.mG_lpf[jump.lowG_range[0]:jump.lowG_range[1]])},'
    line += f'{jump.mG_lpf[jump.lowG_range[0]] if jump.lowG_range[0] == jump.lowG_range[1] else max(jump.mG_lpf[jump.lowG_range[0]:jump.lowG_range[1]])},'
    line += f'{jump.mG_lpf[jump.lowG_range[0]] if jump.lowG_range[0] == jump.lowG_range[1] else mean(jump.mG_lpf[jump.lowG_range[0]:jump.lowG_range[1]])},'
    line += f'{jump.mG_lpf[jump.lowG_range[0]] if jump.lowG_range[0] == jump.lowG_range[1] else std(jump.mG_lpf[jump.lowG_range[0]:jump.lowG_range[1]])},'
    line += f'{jump.mG[jump.lowG_range[0]] if jump.lowG_range[0] == jump.lowG_range[1] else min(jump.mG[jump.lowG_range[0]:jump.lowG_range[1]])},'
    line += f'{jump.mG[jump.lowG_range[0]] if jump.lowG_range[0] == jump.lowG_range[1] else max(jump.mG[jump.lowG_range[0]:jump.lowG_range[1]])},'
    line += f'{jump.mG[jump.lowG_range[0]] if jump.lowG_range[0] == jump.lowG_range[1] else mean(jump.mG[jump.lowG_range[0]:jump.lowG_range[1]])},'
    line += f'{jump.mG[jump.lowG_range[0]] if jump.lowG_range[0] == jump.lowG_range[1] else std(jump.mG[jump.lowG_range[0]:jump.lowG_range[1]])},'
    line += f'{jump.gyro[jump.lowG_range[0]] if jump.lowG_range[0] == jump.lowG_range[1] else min(jump.gyro[jump.lowG_range[0]:jump.lowG_range[1]])},'
    line += f'{jump.gyro[jump.lowG_range[0]] if jump.lowG_range[0] == jump.lowG_range[1] else max(jump.gyro[jump.lowG_range[0]:jump.lowG_range[1]])},'
    line += f'{jump.gyro[jump.lowG_range[0]] if jump.lowG_range[0] == jump.lowG_range[1] else mean(jump.gyro[jump.lowG_range[0]:jump.lowG_range[1]])},'
    line += f'{jump.gyro[jump.lowG_range[0]] if jump.lowG_range[0] == jump.lowG_range[1] else std(jump.gyro[jump.lowG_range[0]:jump.lowG_range[1]])},'
    line += f'{jump.min_idx},'
    line += f'{jump.mG_lpf[jump.min_idx]},'
    line += f'{jump.mG[jump.min_idx]},'
    line += f'{jump.gyro[jump.min_idx]},'
    line += f'{jump.air_range[0]},'
    line += f'{jump.air_range[1]},'
    line += f'{jump.air_range[1] - jump.air_range[0]},'
    line += f'{jump.mG_lpf[jump.air_range[0]] if jump.air_range[0] == jump.air_range[1] else min(jump.mG_lpf[jump.air_range[0]:jump.air_range[1]])},'
    line += f'{jump.mG_lpf[jump.air_range[0]] if jump.air_range[0] == jump.air_range[1] else max(jump.mG_lpf[jump.air_range[0]:jump.air_range[1]])},'
    line += f'{jump.mG_lpf[jump.air_range[0]] if jump.air_range[0] == jump.air_range[1] else mean(jump.mG_lpf[jump.air_range[0]:jump.air_range[1]])},'
    line += f'{jump.mG_lpf[jump.air_range[0]] if jump.air_range[0] == jump.air_range[1] else std(jump.mG_lpf[jump.air_range[0]:jump.air_range[1]])},'
    line += f'{jump.mG[jump.air_range[0]] if jump.air_range[0] == jump.air_range[1] else min(jump.mG[jump.air_range[0]:jump.air_range[1]])},'
    line += f'{jump.mG[jump.air_range[0]] if jump.air_range[0] == jump.air_range[1] else max(jump.mG[jump.air_range[0]:jump.air_range[1]])},'
    line += f'{jump.mG[jump.air_range[0]] if jump.air_range[0] == jump.air_range[1] else mean(jump.mG[jump.air_range[0]:jump.air_range[1]])},'
    line += f'{jump.mG[jump.air_range[0]] if jump.air_range[0] == jump.air_range[1] else std(jump.mG[jump.air_range[0]:jump.air_range[1]])},'
    line += f'{jump.gyro[jump.air_range[0]] if jump.air_range[0] == jump.air_range[1] else min(jump.gyro[jump.air_range[0]:jump.air_range[1]])},'
    line += f'{jump.gyro[jump.air_range[0]] if jump.air_range[0] == jump.air_range[1] else max(jump.gyro[jump.air_range[0]:jump.air_range[1]])},'
    line += f'{jump.gyro[jump.air_range[0]] if jump.air_range[0] == jump.air_range[1] else mean(jump.gyro[jump.air_range[0]:jump.air_range[1]])},'
    line += f'{jump.gyro[jump.air_range[0]] if jump.air_range[0] == jump.air_range[1] else std(jump.gyro[jump.air_range[0]:jump.air_range[1]])},'
    line += f'{jump.liftoff_idx},'
    line += f'{jump.mG_lpf[jump.liftoff_idx]},'
    line += f'{jump.mG[jump.liftoff_idx]},'
    line += f'{jump.gyro[jump.liftoff_idx]},'
    line += f'{jump.touch_idx},'
    line += f'{jump.mG_lpf[jump.touch_idx]},'
    line += f'{jump.mG[jump.touch_idx]},'
    line += f'{jump.gyro[jump.touch_idx]},'
    line += f'{jump.landing_range[0]},'
    line += f'{jump.landing_range[1]},'
    line += f'{jump.landing_range[1] - jump.landing_range[0]},'
    line += f'{jump.mG_lpf[jump.landing_range[0]] if jump.landing_range[0] == jump.landing_range[1] else min(jump.mG_lpf[jump.landing_range[0]:jump.landing_range[1]])},'
    line += f'{jump.mG_lpf[jump.landing_range[0]] if jump.landing_range[0] == jump.landing_range[1] else max(jump.mG_lpf[jump.landing_range[0]:jump.landing_range[1]])},'
    line += f'{jump.mG_lpf[jump.landing_range[0]] if jump.landing_range[0] == jump.landing_range[1] else mean(jump.mG_lpf[jump.landing_range[0]:jump.landing_range[1]])},'
    line += f'{jump.mG_lpf[jump.landing_range[0]] if jump.landing_range[0] == jump.landing_range[1] else std(jump.mG_lpf[jump.landing_range[0]:jump.landing_range[1]])},'
    line += f'{jump.mG[jump.landing_range[0]] if jump.landing_range[0] == jump.landing_range[1] else min(jump.mG[jump.landing_range[0]:jump.landing_range[1]])},'
    line += f'{jump.mG[jump.landing_range[0]] if jump.landing_range[0] == jump.landing_range[1] else max(jump.mG[jump.landing_range[0]:jump.landing_range[1]])},'
    line += f'{jump.mG[jump.landing_range[0]] if jump.landing_range[0] == jump.landing_range[1] else mean(jump.mG[jump.landing_range[0]:jump.landing_range[1]])},'
    line += f'{jump.mG[jump.landing_range[0]] if jump.landing_range[0] == jump.landing_range[1] else std(jump.mG[jump.landing_range[0]:jump.landing_range[1]])},'
    line += f'{jump.gyro[jump.landing_range[0]] if jump.landing_range[0] == jump.landing_range[1] else min(jump.gyro[jump.landing_range[0]:jump.landing_range[1]])},'
    line += f'{jump.gyro[jump.landing_range[0]] if jump.landing_range[0] == jump.landing_range[1] else max(jump.gyro[jump.landing_range[0]:jump.landing_range[1]])},'
    line += f'{jump.gyro[jump.landing_range[0]] if jump.landing_range[0] == jump.landing_range[1] else mean(jump.gyro[jump.landing_range[0]:jump.landing_range[1]])},'
    line += f'{jump.gyro[jump.landing_range[0]] if jump.landing_range[0] == jump.landing_range[1] else std(jump.gyro[jump.landing_range[0]:jump.landing_range[1]])},'
    line += f'{jump.landing_range[1] - jump.air_range[0]},'
    line += f'{jump.mG_lpf[jump.air_range[0]] if jump.air_range[0] == jump.landing_range[1] else min(jump.mG_lpf[jump.air_range[0]:jump.landing_range[1]])},'
    line += f'{jump.mG_lpf[jump.air_range[0]] if jump.air_range[0] == jump.landing_range[1] else max(jump.mG_lpf[jump.air_range[0]:jump.landing_range[1]])},'
    line += f'{jump.mG_lpf[jump.air_range[0]] if jump.air_range[0] == jump.landing_range[1] else mean(jump.mG_lpf[jump.air_range[0]:jump.landing_range[1]])},'
    line += f'{jump.mG_lpf[jump.air_range[0]] if jump.air_range[0] == jump.landing_range[1] else std(jump.mG_lpf[jump.air_range[0]:jump.landing_range[1]])},'
    line += f'{jump.mG[jump.air_range[0]] if jump.air_range[0] == jump.landing_range[1] else min(jump.mG[jump.air_range[0]:jump.landing_range[1]])},'
    line += f'{jump.mG[jump.air_range[0]] if jump.air_range[0] == jump.landing_range[1] else max(jump.mG[jump.air_range[0]:jump.landing_range[1]])},'
    line += f'{jump.mG[jump.air_range[0]] if jump.air_range[0] == jump.landing_range[1] else mean(jump.mG[jump.air_range[0]:jump.landing_range[1]])},'
    line += f'{jump.mG[jump.air_range[0]] if jump.air_range[0] == jump.landing_range[1] else std(jump.mG[jump.air_range[0]:jump.landing_range[1]])},'
    line += f'{jump.gyro[jump.air_range[0]] if jump.air_range[0] == jump.landing_range[1] else min(jump.gyro[jump.air_range[0]:jump.landing_range[1]])},'
    line += f'{jump.gyro[jump.air_range[0]] if jump.air_range[0] == jump.landing_range[1] else max(jump.gyro[jump.air_range[0]:jump.landing_range[1]])},'
    line += f'{jump.gyro[jump.air_range[0]] if jump.air_range[0] == jump.landing_range[1] else mean(jump.gyro[jump.air_range[0]:jump.landing_range[1]])},'
    line += f'{jump.gyro[jump.air_range[0]] if jump.air_range[0] == jump.landing_range[1] else std(jump.gyro[jump.air_range[0]:jump.landing_range[1]])},'
    line += f'{jump.impulse_idx},'
    line += f'{jump.mG_lpf[jump.impulse_idx]},'
    line += f'{jump.mG[jump.impulse_idx]},'
    line += f'{jump.gyro[jump.impulse_idx]},'
    line += f'{jump.distance},'
    line += f'{jump.tests_passed},'
    line += f'{jump.total_tests},'
    line += f'{jump.confidence},'
    line += f'{len(jump.mG_lpf)},'
    line += f'{min(jump.mG_lpf)},'
    line += f'{max(jump.mG_lpf)},'
    line += f'{mean(jump.mG_lpf)},'
    line += f'{std(jump.mG_lpf)},'
    line += f'{min(jump.mG)},'
    line += f'{max(jump.mG)},'
    line += f'{mean(jump.mG)},'
    line += f'{std(jump.mG)},'
    line += f'{min(jump.gyro)},'
    line += f'{max(jump.gyro)},'
    line += f'{mean(jump.gyro)},'
    line += f'{std(jump.gyro)}'
    line += '\n'

    return line


def constructTurnLine(turn: Turn):
    """Constructs the (lengthy) data row based on the turn."""
    shifted_turn_range = [0, len(turn.turn_range) - 1]
    shifted_baseline_range = [0, len(turn.baseline_range) - 1]
    shifted_min_radius_range = [0, len(turn.min_radius_range) - 1]

    line = f'{D_MG_LPF_DT_TH},'
    line += f'{turn.side},'
    line += f'{turn.highG_idx},'
    line += f'{turn.baseline_idx_1},'
    line += f'{turn.baseline_idx_2},'
    line += f'{turn.baseline_idx_3},'
    line += f'{turn.baseline_idx_4},'
    line += f'{turn.baseline_idx_5},'
    line += f'{turn.peak_roll_idx},'
    line += f'{turn.past_peak_roll_idx},'
    line += f'{turn.turn_range[0]},'
    line += f'{turn.turn_range[1]},'
    line += f'{turn.turn_range[1] - turn.turn_range[0]},'
    line += f'{turn.baseline_range[0]},'
    line += f'{turn.baseline_range[1]},'
    line += f'{turn.baseline_range[1] - turn.baseline_range[0]},'
    line += f'{turn.min_radius_range[0]},'
    line += f'{turn.min_radius_range[1]},'
    line += f'{turn.min_radius_range[1] - turn.min_radius_range[0]},'
    line += f'{turn.g_force.mG_lpf[turn.highG_idx]},'
    line += f'{turn.d_boot_roll_dt[turn.highG_idx]},'
    line += f'{turn.offset_abs_roll[-1]},'
    line += f'{turn.g_force.mG_lpf[turn.turn_range[0]] if turn.turn_range[0] == turn.turn_range[1] else min(turn.g_force.mG_lpf[turn.turn_range[0]:turn.turn_range[1]])},'
    line += f'{turn.g_force.mG_lpf[turn.turn_range[0]] if turn.turn_range[0] == turn.turn_range[1] else max(turn.g_force.mG_lpf[turn.turn_range[0]:turn.turn_range[1]])},'
    line += f'{turn.g_force.mG_lpf[turn.turn_range[0]] if turn.turn_range[0] == turn.turn_range[1] else mean(turn.g_force.mG_lpf[turn.turn_range[0]:turn.turn_range[1]])},'
    line += f'{turn.g_force.mG_lpf[turn.turn_range[0]] if turn.turn_range[0] == turn.turn_range[1] else std(turn.g_force.mG_lpf[turn.turn_range[0]:turn.turn_range[1]])},'
    line += f'{turn.g_force.mG_lpf[turn.baseline_range[0]] if turn.baseline_range[0] == turn.baseline_range[1] else min(turn.g_force.mG_lpf[turn.baseline_range[0]:turn.baseline_range[1]])},'
    line += f'{turn.g_force.mG_lpf[turn.baseline_range[0]] if turn.baseline_range[0] == turn.baseline_range[1] else max(turn.g_force.mG_lpf[turn.baseline_range[0]:turn.baseline_range[1]])},'
    line += f'{turn.g_force.mG_lpf[turn.baseline_range[0]] if turn.baseline_range[0] == turn.baseline_range[1] else mean(turn.g_force.mG_lpf[turn.baseline_range[0]:turn.baseline_range[1]])},'
    line += f'{turn.g_force.mG_lpf[turn.baseline_range[0]] if turn.baseline_range[0] == turn.baseline_range[1] else std(turn.g_force.mG_lpf[turn.baseline_range[0]:turn.baseline_range[1]])},'
    line += f'{turn.g_force.mG_lpf[turn.min_radius_range[0]] if turn.min_radius_range[0] == turn.min_radius_range[1] else min(turn.g_force.mG_lpf[turn.min_radius_range[0]:turn.min_radius_range[1]])},'
    line += f'{turn.g_force.mG_lpf[turn.min_radius_range[0]] if turn.min_radius_range[0] == turn.min_radius_range[1] else max(turn.g_force.mG_lpf[turn.min_radius_range[0]:turn.min_radius_range[1]])},'
    line += f'{turn.g_force.mG_lpf[turn.min_radius_range[0]] if turn.min_radius_range[0] == turn.min_radius_range[1] else mean(turn.g_force.mG_lpf[turn.min_radius_range[0]:turn.min_radius_range[1]])},'
    line += f'{turn.g_force.mG_lpf[turn.min_radius_range[0]] if turn.min_radius_range[0] == turn.min_radius_range[1] else std(turn.g_force.mG_lpf[turn.min_radius_range[0]:turn.min_radius_range[1]])},'
    line += f'{turn.offset_abs_roll[shifted_turn_range[0]] if shifted_turn_range[0] == shifted_turn_range[1] else min(turn.offset_abs_roll[shifted_turn_range[0]:shifted_turn_range[1]])},'
    line += f'{turn.offset_abs_roll[shifted_turn_range[0]] if shifted_turn_range[0] == shifted_turn_range[1] else max(turn.offset_abs_roll[shifted_turn_range[0]:shifted_turn_range[1]])},'
    line += f'{turn.offset_abs_roll[shifted_turn_range[0]] if shifted_turn_range[0] == shifted_turn_range[1] else mean(turn.offset_abs_roll[shifted_turn_range[0]:shifted_turn_range[1]])},'
    line += f'{turn.offset_abs_roll[shifted_turn_range[0]] if shifted_turn_range[0] == shifted_turn_range[1] else std(turn.offset_abs_roll[shifted_turn_range[0]:shifted_turn_range[1]])},'
    line += f'{turn.offset_abs_roll[shifted_baseline_range[0]] if shifted_baseline_range[0] == shifted_baseline_range[1] else min(turn.offset_abs_roll[shifted_baseline_range[0]:shifted_baseline_range[1]])},'
    line += f'{turn.offset_abs_roll[shifted_baseline_range[0]] if shifted_baseline_range[0] == shifted_baseline_range[1] else max(turn.offset_abs_roll[shifted_baseline_range[0]:shifted_baseline_range[1]])},'
    line += f'{turn.offset_abs_roll[shifted_baseline_range[0]] if shifted_baseline_range[0] == shifted_baseline_range[1] else mean(turn.offset_abs_roll[shifted_baseline_range[0]:shifted_baseline_range[1]])},'
    line += f'{turn.offset_abs_roll[shifted_baseline_range[0]] if shifted_baseline_range[0] == shifted_baseline_range[1] else std(turn.offset_abs_roll[shifted_baseline_range[0]:shifted_baseline_range[1]])},'
    line += f'{turn.offset_abs_roll[shifted_min_radius_range[0]] if shifted_min_radius_range[0] == shifted_min_radius_range[1] else min(turn.offset_abs_roll[shifted_min_radius_range[0]:shifted_min_radius_range[1]])},'
    line += f'{turn.offset_abs_roll[shifted_min_radius_range[0]] if shifted_min_radius_range[0] == shifted_min_radius_range[1] else max(turn.offset_abs_roll[shifted_min_radius_range[0]:shifted_min_radius_range[1]])},'
    line += f'{turn.offset_abs_roll[shifted_min_radius_range[0]] if shifted_min_radius_range[0] == shifted_min_radius_range[1] else mean(turn.offset_abs_roll[shifted_min_radius_range[0]:shifted_min_radius_range[1]])},'
    line += f'{turn.offset_abs_roll[shifted_min_radius_range[0]] if shifted_min_radius_range[0] == shifted_min_radius_range[1] else std(turn.offset_abs_roll[shifted_min_radius_range[0]:shifted_min_radius_range[1]])},'
    line += f'{turn.d_boot_roll_dt[turn.turn_range[0]] if turn.turn_range[0] == turn.turn_range[1] else min(turn.d_boot_roll_dt[turn.turn_range[0]:turn.turn_range[1]])},'
    line += f'{turn.d_boot_roll_dt[turn.turn_range[0]] if turn.turn_range[0] == turn.turn_range[1] else max(turn.d_boot_roll_dt[turn.turn_range[0]:turn.turn_range[1]])},'
    line += f'{turn.d_boot_roll_dt[turn.turn_range[0]] if turn.turn_range[0] == turn.turn_range[1] else mean(turn.d_boot_roll_dt[turn.turn_range[0]:turn.turn_range[1]])},'
    line += f'{turn.d_boot_roll_dt[turn.turn_range[0]] if turn.turn_range[0] == turn.turn_range[1] else std(turn.d_boot_roll_dt[turn.turn_range[0]:turn.turn_range[1]])},'
    line += f'{turn.d_boot_roll_dt[turn.baseline_range[0]] if turn.baseline_range[0] == turn.baseline_range[1] else min(turn.d_boot_roll_dt[turn.baseline_range[0]:turn.baseline_range[1]])},'
    line += f'{turn.d_boot_roll_dt[turn.baseline_range[0]] if turn.baseline_range[0] == turn.baseline_range[1] else max(turn.d_boot_roll_dt[turn.baseline_range[0]:turn.baseline_range[1]])},'
    line += f'{turn.d_boot_roll_dt[turn.baseline_range[0]] if turn.baseline_range[0] == turn.baseline_range[1] else mean(turn.d_boot_roll_dt[turn.baseline_range[0]:turn.baseline_range[1]])},'
    line += f'{turn.d_boot_roll_dt[turn.baseline_range[0]] if turn.baseline_range[0] == turn.baseline_range[1] else std(turn.d_boot_roll_dt[turn.baseline_range[0]:turn.baseline_range[1]])},'
    line += f'{turn.d_boot_roll_dt[turn.min_radius_range[0]] if turn.min_radius_range[0] == turn.min_radius_range[1] else min(turn.d_boot_roll_dt[turn.min_radius_range[0]:turn.min_radius_range[1]])},'
    line += f'{turn.d_boot_roll_dt[turn.min_radius_range[0]] if turn.min_radius_range[0] == turn.min_radius_range[1] else max(turn.d_boot_roll_dt[turn.min_radius_range[0]:turn.min_radius_range[1]])},'
    line += f'{turn.d_boot_roll_dt[turn.min_radius_range[0]] if turn.min_radius_range[0] == turn.min_radius_range[1] else mean(turn.d_boot_roll_dt[turn.min_radius_range[0]:turn.min_radius_range[1]])},'
    line += f'{turn.d_boot_roll_dt[turn.min_radius_range[0]] if turn.min_radius_range[0] == turn.min_radius_range[1] else std(turn.d_boot_roll_dt[turn.min_radius_range[0]:turn.min_radius_range[1]])},'
    line += f'{turn.alt_lpf[turn.turn_range[0]] if turn.turn_range[0] == turn.turn_range[1] else min(turn.alt_lpf[turn.turn_range[0]:turn.turn_range[1]])},'
    line += f'{turn.alt_lpf[turn.turn_range[0]] if turn.turn_range[0] == turn.turn_range[1] else max(turn.alt_lpf[turn.turn_range[0]:turn.turn_range[1]])},'
    line += f'{turn.alt_lpf[turn.turn_range[0]] if turn.turn_range[0] == turn.turn_range[1] else mean(turn.alt_lpf[turn.turn_range[0]:turn.turn_range[1]])},'
    line += f'{turn.alt_lpf[turn.turn_range[0]] if turn.turn_range[0] == turn.turn_range[1] else std(turn.alt_lpf[turn.turn_range[0]:turn.turn_range[1]])},'
    line += f'{turn.alt_lpf[turn.baseline_range[0]] if turn.baseline_range[0] == turn.baseline_range[1] else min(turn.alt_lpf[turn.baseline_range[0]:turn.baseline_range[1]])},'
    line += f'{turn.alt_lpf[turn.baseline_range[0]] if turn.baseline_range[0] == turn.baseline_range[1] else max(turn.alt_lpf[turn.baseline_range[0]:turn.baseline_range[1]])},'
    line += f'{turn.alt_lpf[turn.baseline_range[0]] if turn.baseline_range[0] == turn.baseline_range[1] else mean(turn.alt_lpf[turn.baseline_range[0]:turn.baseline_range[1]])},'
    line += f'{turn.alt_lpf[turn.baseline_range[0]] if turn.baseline_range[0] == turn.baseline_range[1] else std(turn.alt_lpf[turn.baseline_range[0]:turn.baseline_range[1]])},'
    line += f'{turn.alt_lpf[turn.min_radius_range[0]] if turn.min_radius_range[0] == turn.min_radius_range[1] else min(turn.alt_lpf[turn.min_radius_range[0]:turn.min_radius_range[1]])},'
    line += f'{turn.alt_lpf[turn.min_radius_range[0]] if turn.min_radius_range[0] == turn.min_radius_range[1] else max(turn.alt_lpf[turn.min_radius_range[0]:turn.min_radius_range[1]])},'
    line += f'{turn.alt_lpf[turn.min_radius_range[0]] if turn.min_radius_range[0] == turn.min_radius_range[1] else mean(turn.alt_lpf[turn.min_radius_range[0]:turn.min_radius_range[1]])},'
    line += f'{turn.alt_lpf[turn.min_radius_range[0]] if turn.min_radius_range[0] == turn.min_radius_range[1] else std(turn.alt_lpf[turn.min_radius_range[0]:turn.min_radius_range[1]])},'
    line += f'{turn.carving_angle_1},'
    line += f'{turn.carving_angle_2},'
    line += f'{turn.carving_angle_3},'
    line += f'{turn.carving_angle_4},'
    line += f'{turn.carving_angle_5},'
    line += f'{turn.g_force.mG_lpf[turn.turn_range[0]] if turn.turn_range[0] == turn.turn_range[1] else maxIndex(turn.g_force.mG_lpf[turn.turn_range[0]:turn.turn_range[1]]) - turn.baseline_idx_1},'
    line += f'{maxIndex(turn.offset_abs_roll)},'
    line += f'{turn.d_boot_roll_dt[turn.turn_range[0]] if turn.turn_range[0] == turn.turn_range[1] else maxIndex(turn.d_boot_roll_dt[turn.turn_range[0]:turn.turn_range[1]]) - turn.baseline_idx_1},'
    line += f'{turn.g_force.mG_lpf[turn.turn_range[0]] if turn.turn_range[0] == turn.turn_range[1] else minIndex(turn.g_force.mG_lpf[turn.turn_range[0]:turn.turn_range[1]]) - turn.baseline_idx_1},'
    line += f'{minIndex(turn.offset_abs_roll)},'
    line += f'{turn.d_boot_roll_dt[turn.turn_range[0]] if turn.turn_range[0] == turn.turn_range[1] else minIndex(turn.d_boot_roll_dt[turn.turn_range[0]:turn.turn_range[1]]) - turn.baseline_idx_1}'
    line += '\n'

    return line


def constructSensorBootLines(tile: Tile):
    """Creates the sensor boot frame row."""
    data_dump = ''

    # collect clamped euler data
    sensor_euler = np.apply_along_axis(quatToEuler, 1, tile.imu.quat)
    boot_euler = np.apply_along_axis(quatToEuler, 1, tile.boot_quat)

    for i in range(tile.time.shape[0] - 1):
        q_offset = tile.static_registration.getMostRecentRegistrationQuat(tile.time[i])
        offset_euler = quatToEuler(q_offset)
        
        data_dump += f'{tile.time[i]},{tile.alt_lpf[i]},'
        data_dump += f'{sensor_euler[i, 0]},{sensor_euler[i, 1]},{sensor_euler[i, 2]},'
        data_dump += f'{offset_euler[0]},{offset_euler[1]},{offset_euler[2]},'
        data_dump += f'{boot_euler[i, 0]},{boot_euler[i, 1]},{boot_euler[i, 2]},'
        data_dump += '\n'
    return data_dump