import pytest
from DTC import trajectory, gridsystem
from geopy import distance
from datetime import datetime
from math import sqrt, floor

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
    
    @pytest.fixture
    def five_point_grid(self):
        pc = trajectory.TrajectoryPointCloud()
        t = trajectory.Trajectory()
        
        # Add point to use initialization point
        t.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))

        for i in range(1, 5):
            # Shift points 5 meters north and east (should result in 5 points being 1 cell apart in both x and y)
            shifted_point = distance.distance(meters=i * 5).destination((t.points[0].latitude, t.points[0].longitude), 0)
            shifted_point = distance.distance(meters=i * 5).destination((shifted_point), 90)
        
            t.add_point(shifted_point.longitude, shifted_point.latitude, datetime(2024, 1, 1, 1, 1, 1 + i))
        pc.add_trajectory(t)
        gs = gridsystem.GridSystem(pc)
        gs.create_grid_system()
        return gs

    def test_calculate_index_for_point_is_correct(self, two_point_grid):
        (x1, y1) = two_point_grid.calculate_exact_index_for_point(two_point_grid.pc.trajectories[0].points[0])
        assert (3, 3) == (floor(x1), floor(y1))

        (x2, y2) = two_point_grid.calculate_exact_index_for_point(two_point_grid.pc.trajectories[0].points[1])
        assert (7, 7) == (floor(x2), floor(y2))

    def test_grid_is_build_correctly(self, two_point_grid):
        assert two_point_grid.populated_cells == {(3, 3), (7, 7)}

        assert two_point_grid.pc.trajectories[0].points[0] == two_point_grid.grid[(3, 3)][0]
        assert two_point_grid.pc.trajectories[0].points[1] == two_point_grid.grid[(7, 7)][0]

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

        assert density_center == (3, 3)

    def test_calculate_density_center_returns_correctly_with_two_points(self, two_point_grid):
        density_center1 = two_point_grid.calculate_density_center((3, 3))
        density_center2 = two_point_grid.calculate_density_center((7, 7))

        # Density center should be the same as their neighborhoods intersect and they are the only points
        assert density_center1 == (5, 5)
        assert density_center2 == (5, 5)

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

        density_center1 = gs.calculate_density_center((3, 3))
        density_center2 = gs.calculate_density_center((7, 7))

        # Density center should be skewed towards (3,3) as the quantity of points in this cell is higher
        assert density_center1 == (37 / 11, 37 / 11)
        assert density_center2 == (37 / 11, 37 / 11)

    def test_extract_main_route_returns_correctly_with_single_point(self, single_point_grid):
        single_point_grid.extract_main_route()

        assert single_point_grid.main_route == {(3, 3)}

    def test_extract_main_route_raises_error_correctly(self, single_point_grid):
        with pytest.raises(ValueError) as e:
            single_point_grid.extract_main_route(0.5)
        
        assert str(e.value) == "distance scale must be less than neighborhood size divided by 2"

    def test_extract_main_route_returns_correctly_with_two_points(self, two_point_grid):
        two_point_grid.extract_main_route(0.4)

        assert two_point_grid.main_route == {(3, 3), (7, 7)}

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

        # Density center is skewed towards (3, 3) enough that (6, 6) is not included in main route
        assert gs.main_route == {(3, 3)}

    # Points in grid are not used here as operations are made only on main route
    def test_smooth_main_route_returns_correctly_with_single_element(self, single_point_grid):
        single_point_grid.main_route = {(3, 3)}
        smr = single_point_grid.smooth_main_route()

        # Should simply contain the center of the single cell
        assert smr == {(3.5, 3.5)}

    # Points in grid are not used here as operations are made only on main route
    def test_smooth_main_route_returns_correctly_with_two_elements(self, single_point_grid):
        single_point_grid.main_route = {(3, 3), (27, 3)}
        smr1 = single_point_grid.smooth_main_route()

        # Should only contain the avg position of the two cells centers
        assert smr1 == {(15.5, 3.5)}

        smr2 = single_point_grid.smooth_main_route(20)

        # Should contain the centers of the two cells as they are too far apart
        assert smr2 == {(3.5, 3.5), (27.5, 3.5)}

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

    def test_extract_route_skeleton_returns_correctly_with_many_cells(self, single_point_grid):
        single_point_grid.main_route = set()
        for i in range(1, 27):
            single_point_grid.main_route.add((-24 + 1 * i, 3))

        single_point_grid.main_route.add((-24, 3))
        
        # Add cell more than radius distance from others to not have it be smoothed and therefore later filtered out
        single_point_grid.main_route.add((28, 3))

        single_point_grid.extract_route_skeleton()

        assert (28.5, 3.5) not in single_point_grid.route_skeleton
        assert single_point_grid.route_skeleton != set()

    def test_find_candidate_nearest_neighbors_returns_correctly_with_single_anchor(self, single_point_grid):
        single_point_grid.route_skeleton = {(2, 2)}

        c1 = (1.5, 1.5)
        c2 = (2.5, 2.5)
        c3 = (3.5, 3.5)
        cnn1 = single_point_grid.find_candidate_nearest_neighbors(c1)
        cnn2 = single_point_grid.find_candidate_nearest_neighbors(c2)
        cnn3 = single_point_grid.find_candidate_nearest_neighbors(c3)

        assert cnn1 == {(2, 2)}
        assert cnn2 == {(2, 2)}
        assert cnn3 == {(2, 2)}

    def test_find_candidate_nearest_neighbors_returns_correctly_with_multiple_anchors(self, single_point_grid):
        single_point_grid.route_skeleton = {(2, 2), (2.5, 2.5), (3, 3), (4, 4)}

        c1 = (1.5, 1.5)
        c2 = (2.5, 2.5)
        c3 = (3.5, 3.5)
        cnn1 = single_point_grid.find_candidate_nearest_neighbors(c1)
        cnn2 = single_point_grid.find_candidate_nearest_neighbors(c2)
        cnn3 = single_point_grid.find_candidate_nearest_neighbors(c3)

        assert cnn1 == {(2, 2), (2.5, 2.5)}
        assert cnn2 == {(2, 2), (2.5, 2.5), (3, 3)}
        assert cnn3 == {(2.5, 2.5), (3, 3), (4, 4)}

    def test_find_nearest_neighbor_from_candidates_returns_correctly_with_single_candidate(self, two_point_grid):
        candidates = {(2.5, 2.5)}
        # Point 1 has exact index (3, 3)
        (nn1, d1) = two_point_grid.find_nearest_neighbor_from_candidates(two_point_grid.pc.trajectories[0].points[0], candidates)
        # Point 2 has exact index (7, 7)
        (nn2, d2) = two_point_grid.find_nearest_neighbor_from_candidates(two_point_grid.pc.trajectories[0].points[1], candidates)

        expected_d1 = two_point_grid.calculate_euclidian_distance_between_cells((3, 3), (2.5, 2.5))
        expected_d2 = two_point_grid.calculate_euclidian_distance_between_cells((7, 7), (2.5, 2.5))

        assert (nn1, d1) == ((2.5, 2.5), expected_d1)
        assert (nn2, d2) == ((2.5, 2.5), expected_d2)

    def test_find_nearest_neighbor_from_candidates_returns_correctly_with_two_candidates(self, two_point_grid):
        candidates = {(2.5, 2.5), (5, 6)}
        # Point 1 has exact index (3, 3)
        (nn1, d1) = two_point_grid.find_nearest_neighbor_from_candidates(two_point_grid.pc.trajectories[0].points[0], candidates)
        # Point 2 has exact index (7, 7)
        (nn2, d2) = two_point_grid.find_nearest_neighbor_from_candidates(two_point_grid.pc.trajectories[0].points[1], candidates)

        expected_d1 = two_point_grid.calculate_euclidian_distance_between_cells((3, 3), (2.5, 2.5))
        expected_d2 = two_point_grid.calculate_euclidian_distance_between_cells((7, 7), (5, 6))

        assert (nn1, d1) == ((2.5, 2.5), expected_d1)
        assert (nn2, d2) == ((5, 6), expected_d2)

    def test_find_nearest_neighbor_from_candidates_returns_correctly_with_many_candidates(self, two_point_grid):
        candidates = {(2, 3), (3, 3), (5, 6), (7, 7)}
        # Point 1 has exact index (3, 3)
        (nn1, d1) = two_point_grid.find_nearest_neighbor_from_candidates(two_point_grid.pc.trajectories[0].points[0], candidates)
        # Point 2 has exact index (7, 7)
        (nn2, d2) = two_point_grid.find_nearest_neighbor_from_candidates(two_point_grid.pc.trajectories[0].points[1], candidates)

        expected_d1 = two_point_grid.calculate_euclidian_distance_between_cells((3, 3), (3, 3))
        expected_d2 = two_point_grid.calculate_euclidian_distance_between_cells((7, 7), (7, 7))

        assert (nn1, d1) == ((3, 3), expected_d1)
        assert (nn2, d2) == ((7, 7), expected_d2)        

    def test_create_cover_sets_returns_correctly_with_single_anchor(self, two_point_grid):
        two_point_grid.route_skeleton = {(3, 3)}
        cs = two_point_grid.create_cover_sets()

        expected_d1 = two_point_grid.calculate_euclidian_distance_between_cells((3, 3), (3, 3))
        expected_d2 = two_point_grid.calculate_euclidian_distance_between_cells((7, 7), (3, 3))

        assert len(cs) == 1
        assert cs[(3, 3)] == {(two_point_grid.pc.trajectories[0].points[0], expected_d1), (two_point_grid.pc.trajectories[0].points[1], expected_d2)}

    def test_create_cover_sets_returns_correctly_with_two_anchors(self, two_point_grid):
        two_point_grid.route_skeleton = {(3, 3), (5, 6)}
        cs = two_point_grid.create_cover_sets()

        expected_d1 = two_point_grid.calculate_euclidian_distance_between_cells((3, 3), (3, 3))
        expected_d2 = two_point_grid.calculate_euclidian_distance_between_cells((7, 7), (5, 6))

        assert len(cs) == 2
        assert cs[(3, 3)] == {(two_point_grid.pc.trajectories[0].points[0], expected_d1)}
        assert cs[(5, 6)] == {(two_point_grid.pc.trajectories[0].points[1], expected_d2)}
        assert cs[(3, 3)].isdisjoint(cs[(5, 6)])

    def test_create_cover_sets_returns_correctly_with_multiple_anchors(self, two_point_grid):
        two_point_grid.route_skeleton = {(2, 3), (3, 3), (5, 6), (7, 7)}
        cs = two_point_grid.create_cover_sets()

        expected_d1 = two_point_grid.calculate_euclidian_distance_between_cells((3, 3), (3, 3))
        expected_d2 = two_point_grid.calculate_euclidian_distance_between_cells((7, 7), (7, 7))

        assert len(cs) == 4
        assert cs[(3, 3)] == {(two_point_grid.pc.trajectories[0].points[0], expected_d1)}
        assert cs[(7, 7)] == {(two_point_grid.pc.trajectories[0].points[1], expected_d2)}
        assert cs[(2, 3)] == set()
        assert cs[(5, 6)] == set()
        assert cs[(3, 3)].isdisjoint(cs[(7, 7)])

    def test_construct_safe_areas_returns_correctly_with_two_points_and_single_anchor_and_no_refinement(self, two_point_grid):
        two_point_grid.route_skeleton = {(3, 3)}
        two_point_grid.construct_safe_areas(0)
        
        expected_r = two_point_grid.calculate_euclidian_distance_between_cells((7, 7), (3, 3))

        assert len(two_point_grid.safe_areas) == 1
        assert two_point_grid.safe_areas[(3, 3)] == expected_r

    def test_construct_safe_areas_returns_correctly_with_two_points_and_single_anchor(self, two_point_grid):
        two_point_grid.route_skeleton = {(3, 3)}
        two_point_grid.construct_safe_areas()
        
        expected_r = two_point_grid.calculate_euclidian_distance_between_cells((7, 7), (3, 3)) * 0.99

        assert len(two_point_grid.safe_areas) == 1
        assert two_point_grid.safe_areas[(3, 3)] == expected_r

    def test_construct_safe_areas_returns_correctly_with_five_points_and_single_anchor(self, five_point_grid):
        five_point_grid.route_skeleton = {(3, 3)}
        five_point_grid.construct_safe_areas()
        
        expected_r = five_point_grid.calculate_euclidian_distance_between_cells((7, 7), (3, 3)) * 0.99

        assert len(five_point_grid.safe_areas) == 1
        assert five_point_grid.safe_areas[(3, 3)] == expected_r

        # Now expect 2 points to be removed as noise
        five_point_grid.construct_safe_areas(0.4)
        
        p3 = five_point_grid.calculate_exact_index_for_point(five_point_grid.pc.trajectories[0].points[2])
        distance_to_p3 = five_point_grid.calculate_euclidian_distance_between_cells(p3, (3, 3)) 

        p4 = five_point_grid.calculate_exact_index_for_point(five_point_grid.pc.trajectories[0].points[3])
        distance_to_p4 = five_point_grid.calculate_euclidian_distance_between_cells(p4, (3, 3)) 

        assert len(five_point_grid.safe_areas) == 1
        # As the points are far enough apart, it should result in the 4th point being removed while the 3rd point remains
        # Hence the radius should be smaller than distance to p4 and greater than distance to p3
        assert five_point_grid.safe_areas[(3, 3)] < distance_to_p4
        assert five_point_grid.safe_areas[(3, 3)] > distance_to_p3

    def test_construct_safe_areas_returns_correctly_with_five_points_and_two_anchors(self, five_point_grid):
        # With this split, p1 and p2 belongs to first anchor and p3, p4 and p5 belongs to 2nd anchor
        five_point_grid.route_skeleton = {(2, 2), (7, 7)}
        five_point_grid.construct_safe_areas()
        
        # As mentioned above, the refining radius of safe areas with these splits, will mean that p2 and p3 are removed respectively
        # Thereby yielding radius values just shy of their distance to the anchor points
        p2 = five_point_grid.calculate_exact_index_for_point(five_point_grid.pc.trajectories[0].points[1])
        expected_r1 = five_point_grid.calculate_euclidian_distance_between_cells(p2, (2, 2)) * 0.99

        p3 = five_point_grid.calculate_exact_index_for_point(five_point_grid.pc.trajectories[0].points[2])
        expected_r2 = five_point_grid.calculate_euclidian_distance_between_cells(p3, (7, 7)) * 0.99

        assert len(five_point_grid.safe_areas) == 2
        assert five_point_grid.safe_areas[(2, 2)] == expected_r1
        assert five_point_grid.safe_areas[(7, 7)] == expected_r2