# Skiing Logging

## Goal

To provide more skiing analytics with an extra wearable placed above the ski boot, under the sock. Ideally, this device would publish data:

1. only during ski runs
2. to a parent device, such as an external activity tracker
3. for signals not available from the parent activity tracker

### Signals

- g-force
- turn count
- jump count
- jump distance
- jump height
- ski carving angle

## Devices

Samsung A50 tracking with the SkiApp Pro, which captures complete tracking sets for all stages of a skiing activity. Includes track recognition and is split into 4 categories; downhill, lift, hold, & walk. Other data captured includes global timestamp (in s), 3d distance, 3d velocity, course/heading, altitude, latitude & longitude, and position accuracy (allegedly 2d from GPS). This device will be used as a ground truth to align the tile data through processed pressure data. This device was placed inside the jacket on the torso and had a sampling of 1Hz.

Garmin fenix 6 Pro tracked the activity and represents a more holistic/sport approach towards the track recognition. It only contains recorded data for the downhill portions of the ski activity and therefore won't be used to synchronize the tile data (through pressure/altitude alignment). The tracking itself contains many signals, including all of the A50 data & more. See the parsing notebook for more details. This device was worn on the left wrist and had a sampling of 1Hz.

STM32 SensorTile.Box tracked linear acceleration, angular velocity, magnetic field vectors, temperature, pressure, and humidity signals approximating the right ski. Timestamps are local and require synchronization (see notebook for more) to properly process with the ground truths. Pressure data is also raw and will require an offset to account for sensor differences, weather, etc. which are assumed to be constant for the entire activity. This device was worn tightly under the right sock above the right ski boot, facing laterally. All data signals were sampled at 100Hz

## Data

Data was captured for 6 days of skiing, spread across 2 years and 4 hills/resorts, totalling 100-150 runs.

### Parsing

General process was using notebooks as the background & testing, while finishing up with a function for reuse. Material covered here includes:

- [x] create a common track object containing common props between all devices
- [x] compare the ground truth files
- [x] parse individual data files for a50, f6p, & tile
- [x] synchronize the tile data with mapped global timestamps
  - [x] use the a50 ground truth here since an entire stitched dataset exists & will be more accurate
  - [x] confirm altitude on runs with garmin f6p ground truth
- [x] generate corrected altitude data for the tile mapped from ground truth
- [x] parse the tile data into tracks, focusing on the runs
  - [x] use the garmin timestamps to split since it's a more holistic activity-based approach, plus it's the parent signal you'll be pairing with in the end. Don't see a benefit in recognizing "Hold", "Walk", & "Lift" track types with the tile data. This doesn't work with the older F35 garmin ground truth, which didn't track altitude data.

After these steps, you'll have synchronized signals from each device, which are split into tracks for distinguishing the run data.

### Validation

Not much data crosses over between devices, however we can integrate the 3dof acceleration from the tile and compare it to the a50 & f6p velocities and possibly distance. Note that distance from the other devices is 3d and includes innacuracies in gps position and altitude (baro or mapped).

- [ ] internal integration method to calculate tile velocity (& distance maybe)

### SensorTile Algorithms

Since the estimations explored here will have no ground truths to compare with, this is all in the exploratory phase and will need further testing. Realtime (haptic?) feedback could be designed for the next stage which could provide results while the activity is tracking, ex: vibrate an external wearable on a recognized turn while going downhill.

Added features are aimed to be as low powered as possible, focus on obtaining results from:

- low sampling
- low processing, memory & cpu usage
- least amount of signals/hardware to include

But, for startes a full 6dof and 9dof orientation will be implemented- hopefully leading to correlations in raw signal patterns.

- [ ] orientation algorithms for tile. Not aimed to be in the full wearable, so use a library.
