import numpy as np
from imu import IMU
from registration import Registration
from quat import avgQuat
from sig_proc import maxIndex


class StaticRegistration:
    def __init__(
            self,
            time: np.ndarray,
            alt_lpf: np.ndarray,
            mG: np.ndarray,
            imu: IMU,
            print_out=False,
        ) -> None:
        self.time = time
        self.alt_lpf = alt_lpf
        self.mG = mG
        self.imu = imu

        self.identify(print_out=print_out)


    def liftPeakIdx(self, min_idx=0, window_s=3*60, th=5, within_s=60):
        """Causal!

        Returns the index where a max altitude is reached based on a drop detection within a certain period
        `within_s` seconds and threshold `th`. Begins the index search from the `min_idx` index- default `0`.

        Assumes a ski hill where you begin with a lift! Otherwise, add a delay in `computeCoarseStillRanges()` which 
        calls this function.
        
        Confirms that this is a max over the last period `window_s` seconds.
        """
        dx = 1
        fs = 100
        x = self.alt_lpf[min_idx:]
        for i in range(int(x.shape[0] / dx)):
            i *= dx
            if i < window_s * fs:
                continue
            if x[i - (within_s * fs)] - x[i] > th and x[i - (within_s * fs)] == max(x[i - (window_s * fs):i]):
                return min_idx + i - (within_s * fs)
        return None
    

    def runStartIdx(self, min_idx, th=20, within_s=10):
        """Causal!

        Returns the index where a run begins based on a drop detection within a certain period
        `within_s` seconds and threshold `th`. Begins the index search from the `min_idx` index- default `0`.

        Assumes a ski hill where you begin with a lift! Otherwise, add a delay in `computeCoarseStillRanges()` which 
        calls this function.
        
        Confirms that this is a max over the last period `window_s` seconds.
        """
        dx = 10
        fs = 100
        x = self.alt_lpf[min_idx:]
        for i in range(int(x.shape[0] / dx)):
            i *= dx
            if i < within_s * fs:
                continue
            if x[i - (within_s * fs)] - x[i] > th:
                return min_idx + i - (within_s * fs)
        return None
            
    
    def computeCoarseStillRanges(self, print_out=False):
        self.coarse_ranges = []
        # coarse_addition = 4000
        while True:
            first_idx = self.coarse_ranges[-1][0] if len(self.coarse_ranges) > 0 else 0
            latest_peak = self.liftPeakIdx(min_idx=first_idx)
            if latest_peak is None:
                break
            
            latest_run_start = self.runStartIdx(min_idx=latest_peak)
            if latest_run_start is None:
                break
            
            self.coarse_ranges.append([latest_peak, latest_run_start])
            # coarse_ranges.append([latest_peak, latest_peak + coarse_addition])
            if print_out: print('Coarse static registration range found:', [latest_peak, latest_run_start])
            # if print_out: print('Coarse static registration range found:', [latest_peak, latest_peak + coarse_addition])


    def testMotionForStillness(self, r):
        euler_std_th = 5
        mG_std_th = 200

        # TODO use a non processed signal instead of euler combined
        #  - ifft of raw gyro, accel
        #  - 
        return [
            np.std(self.imu.euler_combined[r[0]:r[1]]) < euler_std_th,
            np.std(self.mG[r[0]:r[1]]) < mG_std_th,
        ]
    

    def computeFineStillRanges(self, min_s=0.25, r=[0, -1], print_out=False) -> list[list]:
        """Identifies ranges of still motion with sampling length `min_s` in seconds
        and returns them as a list of lists representing their indices.
        """
        wsamples = round(min_s * 100)
        search = (r[1] - r[0]) - wsamples
        coarse_mult = wsamples
        fine_mult = round(coarse_mult / 10)
        still_ranges = []
        prev_tail = r[0]
        if search < 0:
            return still_ranges
        
        if print_out:
            print('search:', search)
            print('coarse_mult:', coarse_mult)
            print('fine_mult:', fine_mult)

        for i in range(search):
            if print_out: print('i iter:\t', i)
            for j in range(search):
                # coarse search
                head = prev_tail + coarse_mult * j
                tail = head + wsamples
                
                if tail >= search + r[0]:
                    if print_out: print('\thit the end of the line. tail >= search:', tail, '>=', search + r[0])
                    return still_ranges
                
                trailing_tests = self.testMotionForStillness([head, tail])

                if print_out: print('\tj iter:\t', j)
                if print_out: print('\thead = prev_tail + coarse_mult * j:\t', head, '=', prev_tail, '+', coarse_mult * j)
                if print_out: print('\ttail = head + wsamples:\t', tail, '=', head, '+', wsamples)
                if print_out: print('\tstill_tests:\t', trailing_tests)
                
                if sum(trailing_tests) == len(trailing_tests):
                    if print_out: print('\t\tcoarse range found:\t', head, tail)
                    refinedHead = None
                    refinedTail = None
                    for k in range(search - j):
                        # fine search
                        fine_leading_head = head - fine_mult * (k + 1)
                        fine_leading_tail = tail - fine_mult * (k + 1)
                        fine_trailing_head = head + fine_mult * (k + 1)
                        fine_trailing_tail = tail + fine_mult * (k + 1)

                        if print_out: 
                            print('\t\tk iter:\t', k)
                            print('\t\tfine_leading_head = head - fine_mult * k + 1:\t', fine_leading_head, '=', head, '-', fine_mult, '*', (k + 1))
                            print('\t\tfine_leading_tail = tail - fine_mult * k + 1:\t', fine_leading_tail, '=', tail, '-', fine_mult, '*', (k + 1))
                            print('\t\tfine_trailing_head = head + fine_mult * k + 1:\t', fine_trailing_head, '=', head, '+', fine_mult, '*', (k + 1))
                            print('\t\tfine_trailing_tail = tail + fine_mult * k + 1:\t', fine_trailing_tail, '=', tail, '+', fine_mult, '*', (k + 1))

                        if refinedHead is None:
                            if fine_leading_head <= r[0]:
                                refinedHead = r[0]
                                if print_out: print('\t\t\trefined head set:\t', refinedHead)
                            
                            leading_tests = self.testMotionForStillness([fine_leading_head, fine_leading_tail])
                            if print_out: print('\t\tleading_tests:\t', leading_tests)

                            if sum(leading_tests) < len(leading_tests):
                                refinedHead = fine_leading_head + fine_mult
                                if print_out: print('\t\t\trefined head set:\t', refinedHead)

                        if refinedTail is None:
                            if fine_trailing_tail >= r[1]:
                                refinedTail = r[1]
                                if print_out: print('\t\t\trefined tail set:\t', refinedTail)

                            trailing_tests = self.testMotionForStillness([fine_trailing_head, fine_trailing_tail])
                            if print_out: print('\t\ttrailing_tests:\t', trailing_tests)

                            if sum(trailing_tests) < len(trailing_tests):
                                refinedTail = fine_trailing_tail - fine_mult
                                if print_out: print('\t\t\trefined tail set:\t', refinedTail)

                        if refinedHead is not None and refinedTail is not None:
                            if refinedHead <= prev_tail and len(still_ranges) > 0:
                                if print_out: print('\t\t\tstitched to previous set:\t', [still_ranges[-1][0], refinedTail])
                                still_ranges[-1] = [still_ranges[-1][0], refinedTail]
                            else:
                                if print_out: print('\t\t\trefined still range set:\t', [refinedHead, refinedTail])
                                still_ranges.append([refinedHead, refinedTail])
                            prev_tail = refinedTail
                            break
                    break
        return still_ranges


    def longestFineStillRange(self, r=[0, -1], print_out=False) -> list | None:
        """Uses the coarse range from the lift peak and searches for still ranges, returning the longest range."""
        fine_ranges = self.computeFineStillRanges(r=r, print_out=print_out)
        if print_out: print('Fine static registration ranges:', fine_ranges)
        fine_sizes = [p[1] - p[0] for p in fine_ranges if len(p) > 0]
        return fine_ranges[maxIndex(fine_sizes)] if len(fine_sizes) > 0 else None


    def assignRegistrationsFromRanges(self, print_out=False):
        """Computes the static registration based on the avg orientation within the discovered static
        index `idx`.        
        """
        self.registrations = [
            Registration(
                ts=self.time[r[1]],
                range=r,
                avg_quat=avgQuat(self.imu.quat[r[0]:r[1], :])
            ) for r in self.ranges if r is not None
        ]
        if print_out: print('Identified', len(self.registrations), 'fine static ranges.')


    def identify(self, print_out=False):
        """Identifies first the coarse range fro mthe lift peak, then identifies the longest moment of stillness 
        in that range for an average registration for sensor to boot reorientations.
        """
        if print_out: print('Identifying static ranges up to index:', self.time.shape[0])
        self.computeCoarseStillRanges(print_out=print_out)
        self.ranges = [
            self.longestFineStillRange(r=coarse_range, print_out=print_out) 
            for coarse_range in self.coarse_ranges
        ]
        self.assignRegistrationsFromRanges(print_out=print_out)


    def getMostRecentRegistration(self, timestamp) -> np.ndarray:
        """Gets the most recent registration from `self.registrations` based on `timestamp`.
        
        If any static registration has a associated timestamp lower than the current `timestamp`,
        the registration with the highest timestamp underneath it will be returned.

        If no static registration exists belong the current `timestamp`, it returns a zero
        rotation.
        """
        if timestamp < self.registrations[0].ts:
            return np.array([1, 0, 0, 0])
        
        regs_below = [reg.ts < timestamp for reg in self.registrations]
        return self.registrations[sum(regs_below) - 1].avg_quat


    @property
    def coarse_ranges(self) -> list[list]:
        return self.__coarse_ranges
    
    @coarse_ranges.setter
    def coarse_ranges(self, crs):
        self.__coarse_ranges = crs


    @property
    def ranges(self) -> list[list | None]:
        """The identified ranges of indices that represent a static registration based on the `alt_lpf` signal."""
        return self.__ranges
    
    @ranges.setter
    def ranges(self, rs):
        self.__ranges = rs


    @property
    def registrations(self) -> list[Registration]:
        """The identified static registrations representing the still motions for sensor to boot realignment."""
        return self.__registrations
    
    @registrations.setter
    def registrations(self, rs):
        self.__registrations = rs

