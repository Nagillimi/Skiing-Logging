import numpy as np
from domain.geography.geographical_point import GeographicalPoint
from domain.geography.geographical_search import GeographicalSearch
from domain.geography.geographical_tests import (
    DecreasingSlopeGTTh,
    DecreasingSlopeLTTh,
    IncreasingSlopeGTTh,
    MaxAtBeginningOfPeriod,
    MinAtBeginningOfPeriod,
    SlopeRangeGTTh,
)


class Geography:
    def __init__(
            self,
            time: np.ndarray,
            alt_lpf: np.ndarray,
            print_out=False,
        ) -> None:
        self.time = time
        self.alt_lpf = alt_lpf

        if print_out:
            print('Starting geographical identification, full idx range:', time.shape[0])

        self.lift_bottom_search = GeographicalSearch(
            x=self.alt_lpf, 
            dx=20,
            within_s=60,
            window_s=60,
            tests=[
                IncreasingSlopeGTTh(th=20),
                MinAtBeginningOfPeriod()
            ],
        )
        self.lift_peak_search = GeographicalSearch(
            x=self.alt_lpf, 
            dx=1,
            within_s=60,
            window_s=3*60,
            tests=[
                DecreasingSlopeGTTh(th=5),
                MaxAtBeginningOfPeriod(),
            ],
        )
        self.run_peak_search = GeographicalSearch(
            x=self.alt_lpf, 
            dx=10,
            within_s=10,
            window_s=10,
            tests=[
                DecreasingSlopeGTTh(th=10),
            ],
        )
        self.run_bottom_search = GeographicalSearch(
            x=self.alt_lpf, 
            dx=10,
            within_s=10,
            window_s=30,
            tests=[
                DecreasingSlopeLTTh(th=3),
                SlopeRangeGTTh(th=30),
            ],
        )

        self.identify(print_out=print_out)
        self.patchFragmentedTracks(print_out=print_out)


    def newGeographicalPoint(self, pt_type, idx) -> GeographicalPoint:
        return GeographicalPoint(pt_type, self.time[idx], idx, self.alt_lpf[idx])


    def identify(self, print_out=False):
        """All causal!

        TODO assumes a lift-first based resort
        """
        last_idx = 0
        self.all_points = []
        self.lift_bottoms = []
        self.lift_peaks = []
        self.run_peaks = []
        self.run_bottoms = []
        while True:
            # lift bottom
            latest_lift_bottom_idx = self.lift_bottom_search.search(min_idx=last_idx)
            if latest_lift_bottom_idx is None:
                break
            if print_out:
                print('New geographical point identified | Lift bottom at idx:', latest_lift_bottom_idx)
            new_point = self.newGeographicalPoint('lb', latest_lift_bottom_idx)
            self.all_points.append(new_point)
            self.lift_bottoms.append(new_point)

            # lift peak
            latest_lift_peak_idx = self.lift_peak_search.search(min_idx=latest_lift_bottom_idx)
            if latest_lift_peak_idx is None:
                break
            if print_out:
                print('New geographical point identified | Lift peak at idx:', latest_lift_peak_idx)
            new_point = self.newGeographicalPoint('lp', latest_lift_peak_idx)
            self.all_points.append(new_point)
            self.lift_peaks.append(new_point)

            # run peak
            latest_run_peak_idx = self.run_peak_search.search(min_idx=latest_lift_peak_idx)
            if latest_run_peak_idx is None:
                break
            if print_out:
                print('New geographical point identified | Run peak at idx:', latest_run_peak_idx)
            new_point = self.newGeographicalPoint('rp', latest_run_peak_idx)
            self.all_points.append(new_point)
            self.run_peaks.append(new_point)

            # run bottom
            latest_run_bottom_idx = self.run_bottom_search.search(min_idx=latest_run_peak_idx)
            if latest_run_bottom_idx is None:
                break
            if print_out:
                print('New geographical point identified | Run bottom at idx:', latest_run_bottom_idx)
            new_point = self.newGeographicalPoint('rb', latest_run_bottom_idx)
            self.all_points.append(new_point)
            self.run_bottoms.append(new_point)

            last_idx = latest_run_bottom_idx

        if print_out:
            print('Geographical identification finished.')
            print('\tLift peaks:', len(self.lift_peaks))
            print('\tLift bottoms:', len(self.lift_bottoms))
            print('\tRun peaks:', len(self.run_peaks))
            print('\tRun bottoms:', len(self.run_bottoms))


    def patchFragmentedTracks(self, print_out=False):
        """Fix any situation where a:
        
        - lift bottom is followed by a lift peak
        - run bottom is followed by a run peak
        """
        if print_out:
            print('Correcting any fragmented tracks')

        if len(self.lift_bottoms) != len(self.lift_peaks) or len(self.run_bottoms) != len(self.run_peaks):
            fragments = []
            for i in range(len(self.all_points) - 1):
                if self.all_points[i].pt_type == 'lp' and self.all_points[i + 1].pt_type == 'lb':
                    fragments.append(self.lift_peaks.pop(self.lift_peaks.index(self.all_points[i])))
                    fragments.append(self.lift_peaks.pop(self.lift_bottoms.index(self.all_points[i + 1])))

                if self.all_points[i].pt_type == 'rb' and self.all_points[i + 1].pt_type == 'rp':
                    fragments.append(self.lift_peaks.pop(self.run_bottoms.index(self.all_points[i])))
                    fragments.append(self.lift_peaks.pop(self.run_peaks.index(self.all_points[i + 1])))

            if print_out:
                print('Found and removed', len(fragments), 'fragmented tracks.')

            self.all_points = list(set(self.all_points).symmetric_difference(fragments))
            return
    
        if print_out:
            print('No fragmented tracks found.')
                

    @property
    def lift_bottom_search(self) -> GeographicalSearch:
        """Lift bottom search object and specific parameters."""
        return self.__lift_bottom_search
    
    @lift_bottom_search.setter
    def lift_bottom_search(self, lift_bottom_search):
        self.__lift_bottom_search = lift_bottom_search
        

    @property
    def lift_peak_search(self) -> GeographicalSearch:
        """Lift peak search object and specific parameters."""
        return self.__lift_peak_search
    
    @lift_peak_search.setter
    def lift_peak_search(self, lift_peak_search):
        self.__lift_peak_search = lift_peak_search
        

    @property
    def run_peak_search(self) -> GeographicalSearch:
        """Run peak search object and specific parameters."""
        return self.__run_peak_search
    
    @run_peak_search.setter
    def run_peak_search(self, run_peak_search):
        self.__run_peak_search = run_peak_search
        

    @property
    def run_bottom_search(self) -> GeographicalSearch:
        """Run bottom search object and specific parameters."""
        return self.__run_bottom_search
    
    @run_bottom_search.setter
    def run_bottom_search(self, run_bottom_search):
        self.__run_bottom_search = run_bottom_search
        

    @property
    def all_points(self) -> list[GeographicalPoint]:
        """List of all geographical points identified by all search tests, ordered sequentially."""
        return self.__all_points
    
    @all_points.setter
    def all_points(self, all_points):
        self.__all_points = all_points
        

    @property
    def lift_bottoms(self) -> list[GeographicalPoint]:
        """List of lift bottoms identified by the lift bottom search."""
        return self.__lift_bottoms
    
    @lift_bottoms.setter
    def lift_bottoms(self, lift_bottoms):
        self.__lift_bottoms = lift_bottoms
        

    @property
    def lift_peaks(self) -> list[GeographicalPoint]:
        """List of lift peaks identified by the lift peak search."""
        return self.__lift_peaks
    
    @lift_peaks.setter
    def lift_peaks(self, lift_peaks):
        self.__lift_peaks = lift_peaks
        

    @property
    def run_peaks(self) -> list[GeographicalPoint]:
        """List of run peaks identified by the run peak search."""
        return self.__run_peaks
    
    @run_peaks.setter
    def run_peaks(self, run_peaks):
        self.__run_peaks = run_peaks


    @property
    def run_bottoms(self) -> list[GeographicalPoint]:
        """List of run bottoms identified by the run bottom search."""
        return self.__run_bottoms
    
    @run_bottoms.setter
    def run_bottoms(self, run_bottoms):
        self.__run_bottoms = run_bottoms
