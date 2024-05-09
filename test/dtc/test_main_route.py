import pytest
from DTC.construct_main_route import ConstructMainRoute
from DTC.trajectory import Trajectory, TrajectoryPointCloud
from DTC.gridsystem import GridSystem
from DTC.gridsystem import DistanceCalculator

class test_construct_main_route:
    @pytest.fixture
    def single_point_grid(self):
        pc = TrajectoryPointCloud()
        t = Trajectory()
        
        # Add point to use initialization point
        t.add_point(1,0)

        pc.add_trajectory(t)
        gs = GridSystem(pc)
        gs.create_grid_system()
        return gs

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
        pc.add_trajectory(t)
        gs = GridSystem(pc)
        gs.create_grid_system()
        return gs

    def test_calculate_density_center_returns_correctly_with_single_point(self, single_point_grid):
        density_center = ConstructMainRoute.calculate_density_center((4, 4), single_point_grid.populated_cells, single_point_grid.grid)

        assert density_center == (4, 4)

    def test_calculate_density_center_returns_correctly_with_two_points(self, two_point_grid):
        density_center1 = ConstructMainRoute.calculate_density_center((4, 4), two_point_grid.populated_cells, two_point_grid.grid)
        density_center2 = ConstructMainRoute.calculate_density_center((8, 8), two_point_grid.populated_cells, two_point_grid.grid)

        # Density center should be the same as their neighborhoods intersect and they are the only points
        assert density_center1 == (5, 5)
        assert density_center2 == (5, 5)

    def test_calculate_density_center_returns_correctly_with_many_points(self):
        pc = TrajectoryPointCloud()
        t = Trajectory()
        
        # Add point to use initialization point
        for _ in range(1, 11):
            t.add_point(1,0)

        # Shift second point 20 meters north and east (should result in the two points being 4 cells apart in both x and y)
        shifted_point = DistanceCalculator.shift_point_with_bearing(t.points[0], 20, DistanceCalculator.NORTH)
        shifted_point = DistanceCalculator.shift_point_with_bearing(shifted_point, 20, DistanceCalculator.EAST)
        t.add_point(shifted_point[0], shifted_point[1])

        pc.add_trajectory(t)
        gs = GridSystem(pc)
        gs.create_grid_system()

        density_center1 = ConstructMainRoute.calculate_density_center((3, 3), gs.populated_cells, gs.grid)
        density_center2 = ConstructMainRoute.calculate_density_center((7, 7), gs.populated_cells, gs.grid)

        # Density center should be skewed towards (3,3) as the quantity of points in this cell is higher
        assert density_center1 == (37 / 11, 37 / 11)
        assert density_center2 == (37 / 11, 37 / 11)

