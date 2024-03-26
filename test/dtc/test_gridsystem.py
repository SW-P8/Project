import pytest
from DTC import trajectory, gridsystem
from geopy import distance
from datetime import datetime
from math import sqrt

class TestGridsystem():
    @pytest.fixture
    def single_point_grid(self):
        pc = trajectory.TrajectoryPointCloud()
        t = trajectory.Trajectory()
        
        # Add point to use initialization point
        t.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))

        pc.add_trajectory(t)
        gs = gridsystem.GridSystem(pc)
        gs.create_grid_system()
        return gs

    @pytest.fixture
    def two_point_grid(self):
        pc = trajectory.TrajectoryPointCloud()
        t = trajectory.Trajectory()
        
        # Add point to use initialization point
        t.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))

        # Shift second point 20 meters north and east (should result in the two points being 4 cells apart in both x and y)
        shifted_point = distance.distance(meters=20).destination((t.points[0].latitude, t.points[0].longitude), 0)
        shifted_point = distance.distance(meters=20).destination((shifted_point), 90)
        
        t.add_point(shifted_point.longitude, shifted_point.latitude, datetime(2024, 1, 1, 1, 1, 2))
        pc.add_trajectory(t)
        gs = gridsystem.GridSystem(pc)
        gs.create_grid_system()
        return gs

    def test_calculate_index_for_point_is_correct(self, two_point_grid):
        (x1, y1) = two_point_grid.calculate_index_for_point(two_point_grid.pc.trajectories[0].points[0])
        assert (2, 3) == (x1, y1)

        (x2, y2) = two_point_grid.calculate_index_for_point(two_point_grid.pc.trajectories[0].points[1])
        assert (6, 6) == (x2, y2)

    def test_grid_is_build_correctly(self, two_point_grid):
        actual_x_size = len(two_point_grid.grid)
        assert actual_x_size == 13

        actual_y_size = len(two_point_grid.grid[0])
        assert actual_y_size == 12

        assert two_point_grid.populated_cells == {(2, 3), (6, 6)}

        assert two_point_grid.pc.trajectories[0].points[0] == two_point_grid.grid[2][3][0]
        assert two_point_grid.pc.trajectories[0].points[1] == two_point_grid.grid[6][6][0]

    def test_calculate_euclidian_distance_returns_correctly(self):
        c1 = (0, 0)
        c2 = (1, 0)
        c3 = (0, 1)
        c4 = (1, 1)

        d_c1_c1 = gridsystem.GridSystem.calculate_euclidian_distance_between_cells(c1, c1)
        d_c1_c2 = gridsystem.GridSystem.calculate_euclidian_distance_between_cells(c1, c2)
        d_c1_c3 = gridsystem.GridSystem.calculate_euclidian_distance_between_cells(c1, c3)
        d_c1_c4 = gridsystem.GridSystem.calculate_euclidian_distance_between_cells(c1, c4)


        assert d_c1_c1 == 0
        assert d_c1_c2 == 1
        assert d_c1_c3 == 1
        assert d_c1_c4 == sqrt(2)

    def test_calculate_density_center_returns_correctly_with_single_point(self, single_point_grid):
        density_center = single_point_grid.calculate_density_center((2, 3))

        assert density_center == (2, 3)

    def test_calculate_density_center_returns_correctly_with_two_points(self, two_point_grid):
        density_center1 = two_point_grid.calculate_density_center((2, 3))
        density_center2 = two_point_grid.calculate_density_center((6, 6))

        # Density center should be the same as their neighborhoods intersect and they are the only points
        assert density_center1 == (4, 4.5)
        assert density_center2 == (4, 4.5)

    def test_calculate_density_center_returns_correctly_with_many_points(self):
        pc = trajectory.TrajectoryPointCloud()
        t = trajectory.Trajectory()
        
        # Add point to use initialization point
        for i in range(1, 11):
            t.add_point(1,0,datetime(2024, 1, 1, 1, 1, i))

        # Shift second point 20 meters north and east (should result in the two points being 4 cells apart in both x and y)
        shifted_point = distance.distance(meters=20).destination((t.points[0].latitude, t.points[0].longitude), 0)
        shifted_point = distance.distance(meters=20).destination((shifted_point), 90)
        t.add_point(shifted_point.longitude, shifted_point.latitude, datetime(2024, 1, 1, 1, 1, 11))


        pc.add_trajectory(t)
        gs = gridsystem.GridSystem(pc)
        gs.create_grid_system()

        density_center1 = gs.calculate_density_center((2, 3))
        density_center2 = gs.calculate_density_center((6, 6))

        # Density center should be skewed towards (2,3) as the quantity of points in this cell is higher
        assert density_center1 == (26 / 11, 36 / 11)
        assert density_center2 == (26 / 11, 36 / 11)

    def test_extract_main_route_returns_correctly_with_single_point(self, single_point_grid):
        single_point_grid.extract_main_route()

        assert single_point_grid.main_route == {(2, 3)}

    def test_extract_main_route_raises_error_correctly(self, single_point_grid):
        with pytest.raises(ValueError) as e:
            single_point_grid.extract_main_route(0.5)
        
        assert str(e.value) == "distance scale must be less than neighborhood size divided by 2"

    def test_extract_main_route_returns_correctly_with_two_points(self, two_point_grid):
        two_point_grid.extract_main_route(0.4)

        assert two_point_grid.main_route == {(2, 3), (6, 6)}

        # Should return an empty set with default d
        two_point_grid.extract_main_route()
        assert two_point_grid.main_route == set()

    def test_extract_main_route_returns_correctly_with_many_points(self):
        pc = trajectory.TrajectoryPointCloud()
        t = trajectory.Trajectory()
        
        # Add point to use initialization point
        for i in range(1, 11):
            t.add_point(1,0,datetime(2024, 1, 1, 1, 1, i))

        # Shift second point 20 meters north and east (should result in the two points being 4 cells apart in both x and y)
        shifted_point = distance.distance(meters=20).destination((t.points[0].latitude, t.points[0].longitude), 0)
        shifted_point = distance.distance(meters=20).destination((shifted_point), 90)
        t.add_point(shifted_point.longitude, shifted_point.latitude, datetime(2024, 1, 1, 1, 1, 11))


        pc.add_trajectory(t)
        gs = gridsystem.GridSystem(pc)
        gs.create_grid_system()
        gs.extract_main_route()

        # Density center is skewed towards (2, 3) enough that (6, 6) is not included in main route
        assert gs.main_route == {(2, 3)}

    # Points in grid are not used here as operations are made only on main route
    def test_smooth_main_route_returns_correctly_with_single_element(self, single_point_grid):
        single_point_grid.main_route = {(2, 3)}
        smr = single_point_grid.smooth_main_route()

        # Should simply contain the center of the single cell
        assert smr == {(2.5, 3.5)}

    # Points in grid are not used here as operations are made only on main route
    def test_smooth_main_route_returns_correctly_with_two_elements(self, single_point_grid):
        single_point_grid.main_route = {(2, 3), (27, 3)}
        smr1 = single_point_grid.smooth_main_route()

        # Should only contain the avg position of the two cells centers
        assert smr1 == {(15, 3.5)}

        smr2 = single_point_grid.smooth_main_route(20)

        # Should contain the centers of the two cells as they are too far apart
        assert smr2 == {(2.5, 3.5), (27.5, 3.5)}

    # Points in grid are not used here as operations are made only on main route
    def test_smooth_main_route_returns_correctly_with_multiple_elements(self, single_point_grid):
        single_point_grid.main_route = {(2, 3), (27, 3), (32, 3)}
        smr = single_point_grid.smooth_main_route()

        # Should only contain 3 positions        
        assert smr == {(15, 3.5), ((2.5 + 27.5 + 32.5)/3, 3.5), (30, 3.5)}

    # Points in grid are not used here as operations are made only on main route
    def test_filter_outliers_in_main_route_returns_correctly_with_single_element(self, single_point_grid):
        smr = {(2.5, 3.5)}
        cmr = single_point_grid.filter_outliers_in_main_route(smr)
        assert cmr == {(2.5, 3.5)}

    # Points in grid are not used here as operations are made only on main route
    def test_filter_outliers_in_main_route_filters_outlier_correctly(self, single_point_grid):
        smr = set()
        for i in range(1, 101):
            smr.add((1 + 0.01 * i, 3.5))
        
        # Add cell more than radius prime distance from others
        smr.add((23, 3.5))
        cmr = single_point_grid.filter_outliers_in_main_route(smr)

        # Check that outlier cell is correctly removed
        assert (23, 3.5) not in cmr
        assert smr - cmr == {(23, 3.5)}

    # Points in grid are not used here as operations are made only on main route
    def test_filter_outliers_in_main_route_returns_correctly_with_multiple_elements(self, single_point_grid):
        smr = set()
        for i in range(1, 101):
            smr.add((1 + 0.01 * i, 3.5))
        
        # Add two cell more than radius prime distance from others (should be enough to not be filtered out)
        smr.add((23, 3.5))
        smr.add((23.1, 3.5))
        cmr = single_point_grid.filter_outliers_in_main_route(smr)

        # Check that the two far cells are not removed
        assert (23, 3.5) in cmr
        assert (23.1, 3.5) in cmr
        assert smr - cmr == set()

    # Points in grid are not used here as operations are made only on main route
    def test_sample_main_route_returns_correctly_with_single_cell(self, single_point_grid):
        cmr = {(2, 3)}
        rs = single_point_grid.sample_main_route(cmr)
        assert rs == set()

    # Points in grid are not used here as operations are made only on main route
    def test_sample_main_route_returns_correctly_with_two_cells(self, single_point_grid):
        cmr = {(2, 3), (22, 3)}
        rs1 = single_point_grid.sample_main_route(cmr)
        assert rs1 == {(2, 3), (22, 3)}

        rs2 = single_point_grid.sample_main_route(cmr, 19)
        assert rs2 == set()

    # Points in grid are not used here as operations are made only on main route
    def test_sample_main_route_returns_correctly(self, single_point_grid):
        cmr = set()
        for i in range(1, 101):
            cmr.add((1 + 0.01 * i, 3.5))
        
        # Add cell a large distance from others
        cmr.add((23, 3.5))
        rs = single_point_grid.sample_main_route(cmr)

        # Check that outlier cell is correctly removed
        assert (23, 3.5) not in rs
        assert cmr - rs == {(23, 3.5)}

    def test_extract_route_skeleton_returns_correctly_with_single_cell(self, single_point_grid):
        single_point_grid.main_route = {(2, 3)}
        single_point_grid.extract_route_skeleton()
        assert single_point_grid.route_skeleton == set()

    def test_extract_route_skeleton_returns_correctly_with_two_cells(self, single_point_grid):
        single_point_grid.main_route = {(2, 3), (12, 3)}
        single_point_grid.extract_route_skeleton()
        assert single_point_grid.route_skeleton == set()

    def test_extract_route_skeleton_returns_correctly_with_three_cells(self, single_point_grid):
        single_point_grid.main_route = {(2, 3), (27, 3), (32, 3)}
        single_point_grid.extract_route_skeleton()
        assert single_point_grid.route_skeleton == {(15, 3.5), ((2.5 + 27.5 + 32.5)/3, 3.5), (30, 3.5)}

    def test_extract_route_skeleton_returns_correctly_with_two_cells(self, single_point_grid):
        single_point_grid.main_route = set()
        for i in range(1, 27):
            single_point_grid.main_route.add((-24 + 1 * i, 3))

        single_point_grid.main_route.add((-24, 3))
        
        # Add cell more than radius distance from others to not have it be smoothed and therefore later filtered out
        single_point_grid.main_route.add((28, 3))

        single_point_grid.extract_route_skeleton()

        assert (28.5, 3.5) not in single_point_grid.route_skeleton
        assert single_point_grid.route_skeleton != set()