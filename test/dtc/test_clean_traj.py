import pytest
from DTC import gridsystem, trajectory
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
    t.add_point(1,1)

    for i in range(1, 5):
        # Shift points 5 meters north and east (should result in 5 points being 1 cell apart in both x and y)
        shifted_point = DistanceCalculator.shift_point_with_bearing(t.points[0], i * 5, DistanceCalculator.NORTH)
        shifted_point = DistanceCalculator.shift_point_with_bearing(shifted_point, i * 5, DistanceCalculator.EAST)
        
        t.add_point(shifted_point[0], shifted_point[1])
    pc.add_trajectory(t)
    gs = gridsystem.GridSystem(pc)
    gs.initialization_point = (0, 0)
    gs.safe_areas = {
            (1,1): SafeArea({(0,1),(0,2)}, anchor=(1, 1), decrease_factor=0.1),
            (0,1): SafeArea({(1,1),(0,2)}, anchor=(0, 1), decrease_factor=0.1),
            (0,2): SafeArea({(1,1),(0,1)}, anchor=(0, 2), decrease_factor=0.1),
            }
    for _,v in gs.safe_areas.items():
        v.radius = 10
    return gs

@pytest.fixture
def points():
    return [Point(116.37677,39.88791), Point(116.38033,39.88795), Point(116.39392,39.89014)]

# Tests for the CleanTraj class
class TestCleanTraj:
    def test_init(self, grid_system):
        clean_traj = CleanTraj(grid_system)
        assert clean_traj.gridsystem == grid_system
        assert isinstance(clean_traj.safe_areas, dict)

    def test_clean(self,grid_system, points):
        clean_traj = CleanTraj(grid_system)

        clean_traj.clean(points)
        print(clean_traj)
        

    def test_incremental_refine(self, grid_system):
        point = Point(0.1, 11.0)
        safe_area = SafeArea({(0,1),(1,1),(0,1)}, anchor=(0, 0), decrease_factor=0.1)
        safe_area.radius = 30
        clean_traj = CleanTraj(grid_system)

        clean_traj.incremental_refine(safe_area, point, grid_system.initialization_point)

