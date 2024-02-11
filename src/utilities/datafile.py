import os
import numpy as np
from domain.jump import JUMP_THRESHOLD_MG, Jump
from domain.tile import Tile
from utilities.quat import quatToEuler
from utilities.sig_proc import mean, std


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


SENSOR_BOOT_HEADER = 'time [s],alt_lpf [m],sensor_roll,sensor_pitch,sensor_yaw,'\
    + 'offset_roll,offset_pitch,offset_yaw,'\
    + 'boot_roll,boot_pitch,boot_yaw,'\
    + '\n'


def createDataFile(name, header):
    """Creates a generic data file inside the `logs/` dir.
    
    Checks that the logs dir exists, if not creates it.

    Checks to see if the logfile already exists, then overwrites it.
    """
    # single log file across all tracks, used to train future ml models
    if not os.path.exists(os.path.join(os.getcwd().split('src')[0], 'logs')):
        os.mkdir(os.path.join(os.getcwd().split('src')[0], 'logs'))
    
    # delete previous file with matching name
    if os.path.exists(os.path.join(os.getcwd().split('src')[0], 'logs/', name)):
        os.remove(os.path.join(os.getcwd().split('src')[0], 'logs/', name))

    file_train = open(os.path.join(os.getcwd().split('src')[0], 'logs/', name), "w")
    file_train.write(header)
    return file_train


def createJumpDataFile(name):
    """Creates a specific logfile for jump data."""
    return createDataFile(name, JUMP_HEADER)


def createSensorBootDataFile(name):
    """Creates a specific logfile for sensor boot frame data."""
    return createDataFile(name, SENSOR_BOOT_HEADER)


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