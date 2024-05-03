import pytest
from datetime import datetime
from DTC.gridsystem import GridSystem
from DTC.trajectory import TrajectoryPointCloud, Trajectory
from DTC.distance_calculator import DistanceCalculator
from DTC.clean import CleanTraj
from DTC.construct_safe_area import SafeArea, Point

# Fixtures for GridSystem and Point objects
@pytest.fixture
def grid_system():
    pc = TrajectoryPointCloud()
    t = Trajectory()
        
    # Add point to use initialization point
    t.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))

    for i in range(1, 5):
        # Shift points 5 meters north and east (should result in 5 points being 1 cell apart in both x and y)
        shifted_point = DistanceCalculator.shift_point_with_bearing(t.points[0], i * 5, DistanceCalculator.NORTH)
        shifted_point = DistanceCalculator.shift_point_with_bearing(shifted_point, i * 5, DistanceCalculator.EAST)
        
        t.add_point(shifted_point[0], shifted_point[1], datetime(2024, 1, 1, 1, 1, 1 + i))
    pc.add_trajectory(t)
    gs = GridSystem(pc)
    gs.create_grid_system()
    gs.extract_main_route()
    gs.extract_route_skeleton()
    gs.construct_safe_areas()
    for _,safe_area in gs.safe_areas.items():
        safe_area.radius = 5
        safe_area.timestamp = datetime.now()
        safe_area.cardinality = 69 + 420 
    return gs

@pytest.fixture
def points():
    return [Point(116.37677,39.88791, datetime.now()), Point(116.38033,39.88795,datetime.now()), Point(116.39392,39.89014,datetime.now())]

# Tests for the CleanTraj class
class TestCleanTraj:
    def test_init(self, grid_system : GridSystem):
        clean_traj = CleanTraj(grid_system.safe_areas, grid_system.route_skeleton, grid_system.initialization_point)
        assert clean_traj.initialization_point == grid_system.initialization_point
        assert clean_traj.route_skeleton == grid_system.route_skeleton
        assert isinstance(clean_traj.safe_areas, dict)

    def test_clean(self,grid_system, points):
        clean_traj = CleanTraj(grid_system.safe_areas, grid_system.route_skeleton, grid_system.initialization_point)

        clean_traj.clean(points)
        

    def test_incremental_refine(self, grid_system):
        point = Point(0.1, 11.0)
        safe_area = SafeArea({(0,1),(1,1),(0,1)}, anchor=(0, 0), decrease_factor=0.1)
        safe_area.radius = 30
        clean_traj = CleanTraj(grid_system.safe_areas, grid_system.route_skeleton, grid_system.initialization_point)

        clean_traj.incremental_refine(safe_area, point, grid_system.initialization_point)
        