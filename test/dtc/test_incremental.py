import pytest
from datetime import datetime, timedelta
from DTC.construct_safe_area import SafeArea
from DTC.distance_calculator import DistanceCalculator
from DTC.trajectory import Trajectory, TrajectoryPointCloud
from DTC.gridsystem import GridSystem
from DTC.incremental import Incremental
from DTC.point import Point

class TestIncremental():
    @pytest.fixture
    def two_point_grid(self):
        pc = TrajectoryPointCloud()
        t = Trajectory()
        
        # Add point to use initialization point
        t.add_point(1,0)

        # Shift second point 20 meters north and east (should result in the two points being 4 cells apart in both x and y)
        DistanceCalculator.shift_point_with_bearing(t.points[0], 20, DistanceCalculator.NORTH)
        shifted_point = DistanceCalculator.shift_point_with_bearing(t.points[0], 20, DistanceCalculator.NORTH)
        shifted_point = DistanceCalculator.shift_point_with_bearing(shifted_point, 20, DistanceCalculator.EAST)

        t.add_point(shifted_point[0], shifted_point[1])

        DistanceCalculator.shift_point_with_bearing(t.points[1], 20, DistanceCalculator.NORTH)
        shifted_point = DistanceCalculator.shift_point_with_bearing(t.points[1], 20, DistanceCalculator.NORTH)
        shifted_point = DistanceCalculator.shift_point_with_bearing(shifted_point, 20, DistanceCalculator.EAST)

        t.add_point(shifted_point[0], shifted_point[1])

        pc.add_trajectory(t)
        gs = GridSystem(pc)
        gs.create_grid_system()
        
        cs1 = set()
        cs1.add((0,0))

        cs2 = set()
        cs2.add((20,20))

        gs.safe_areas[(3,3)] = SafeArea(cs1, (3,3), 0)
        gs.safe_areas[(3,3)].radius = 1
        gs.safe_areas[(7,7)] = SafeArea(cs2, (7,7), 0)
        gs.safe_areas[(7,7)].radius = 1

        return gs

    def test_incremental_outlier_with_two_safe_areas(self, two_point_grid):
        sa = two_point_grid.safe_areas
        sa[(7,7)].cardinality = 10
        inc = Incremental(sa)
        inc.incremental_refine(two_point_grid.pc.trajectories[0].points[2], two_point_grid.initialization_point)
        
        assert inc.safe_areas[(7,7)].confidence < 1.0
        assert len(inc.noisy_points) == 1

    def test_incremental_correct_point_with_two_safe_areas_high_frequency_inserts(self, two_point_grid):
        sa = two_point_grid.safe_areas
        inc = Incremental(sa)
        inc.safe_areas[(3,3)].timestamp = datetime.now()
        inc.incremental_refine(two_point_grid.pc.trajectories[0].points[0], two_point_grid.initialization_point)

        #Test for insertion when cardinality for SA is 1
        print(f'Confidence = {inc.safe_areas[(3,3)].confidence}')
        assert inc.safe_areas[(3,3)].confidence >= 1.0
        assert len(inc.noisy_points) == 0

        #Test for insertion when cardinality for SA is 100
        inc.safe_areas[(3,3)].cardinality = 100
        inc.safe_areas[(3,3)].timestamp = datetime.now()
        inc.incremental_refine(two_point_grid.pc.trajectories[0].points[0], two_point_grid.initialization_point)
        print(f'Confidence = {inc.safe_areas[(3,3)].confidence}')
    
        assert inc.safe_areas[(3,3)].confidence >= 1.0
        assert len(inc.noisy_points) == 0

        #Test for insertion when cardinality for SA is 1000
        inc.safe_areas[(3,3)].cardinality = 1000
        inc.safe_areas[(3,3)].timestamp = datetime.now()
        inc.incremental_refine(two_point_grid.pc.trajectories[0].points[0], two_point_grid.initialization_point)
        print(f'Confidence = {inc.safe_areas[(3,3)].confidence}')
    
        assert inc.safe_areas[(3,3)].confidence >= 1.0
        assert len(inc.noisy_points) == 0

        #Test for insertion when cardinality for SA is 20000
        inc.safe_areas[(3,3)].cardinality = 20000
        inc.safe_areas[(3,3)].timestamp = datetime.now()
        inc.incremental_refine(two_point_grid.pc.trajectories[0].points[0], two_point_grid.initialization_point)
        print(f'Confidence20000 = {inc.safe_areas[(3,3)].confidence}')
        inc.incremental_refine(two_point_grid.pc.trajectories[0].points[0], two_point_grid.initialization_point)
        print(f'Confidence20001 = {inc.safe_areas[(3,3)].confidence}')

        assert inc.safe_areas[(3,3)].confidence >= 1.0
        assert len(inc.noisy_points) == 0

    def test_incremental_correct_points_with_large_time_intervals(self, two_point_grid):
        sa = two_point_grid.safe_areas
        inc = Incremental(sa)
        td = timedelta(hours=12)
        ts = datetime.now() - td
        inc.safe_areas[(3,3)].timestamp = ts
        
        inc.incremental_refine(two_point_grid.pc.trajectories[0].points[0], two_point_grid.initialization_point)

        #Test for insertion when cardinality for SA is 1
        print(f'Confidence = {inc.safe_areas[(3,3)].confidence}')
        assert inc.safe_areas[(3,3)].confidence < 1.0 #A safe area should probably lose confidence if it only gets one point every 12 hours.  
        assert inc.safe_areas[(3,3)].confidence > 0.85
        assert len(inc.noisy_points) == 0
        assert False

