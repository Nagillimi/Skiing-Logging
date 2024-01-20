import os

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
    

def createDataFile(name, header):
    """Creates a generic data file inside the `logs/` dir.
    
    Checks that the logs dir exists, if not creates it.

    Checks to see if the logfile already exists, then overwrites it.
    """
    # single log file across all tracks, used to train future ml models
    if not os.path.exists(os.path.join(os.getcwd(), 'logs')):
        os.mkdir(os.path.join(os.getcwd(), 'logs'))
    
    # delete previous file with matching name
    if os.path.exists(os.path.join(os.getcwd(), name)):
        os.remove(os.path.join(os.getcwd(), name))

    file_train = open(name, "w")
    file_train.write(header)
    return file_train


def createJumpDataFile(name):
    """Creates a specific logfile for jump data."""
    return createDataFile(name, JUMP_HEADER)