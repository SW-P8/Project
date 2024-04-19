from DTC.route_skeleton import RouteSkeleton
from collections import defaultdict
from math import floor
from copy import deepcopy

class TestRouteSkeleton():
    def test_smooth_main_route_returns_correctly_with_single_element(self):
        # Arrange
        main_route = {(3, 3)}
        expected = {(3.5, 3.5)}

        # Act
        result = RouteSkeleton.smooth_main_route(main_route, 25)

        # Should simply contain the center of the single cell
        assert result == expected

    def test_smooth_main_route_returns_correctly_with_two_elements(self):
        # Arrange
        main_route = {(3, 3), (27, 3)}
        expected = {(15.5, 3.5)}
        expected2 = {(3.5, 3.5),(27.5, 3.5)}

        # Act
        result = RouteSkeleton.smooth_main_route(main_route, 25)
        result2 = RouteSkeleton.smooth_main_route(main_route, 20)

        # Assert
        assert result == expected #should only contain the avg position of the two cells centers
        assert result2 == expected2 #should contain the centers of the two cells as they are too far apart

    def test_smooth_main_route_returns_correctly_with_multiple_elements(self):
        # Arrange
        main_route = {(2, 3), (27, 3), (32, 3)}
        expected = {(15, 3.5), (20.83, 3.5), (30, 3.5)}

        # Act
        result = RouteSkeleton.smooth_main_route(main_route, 25)

        # Assert        
        assert result == expected #should only contain 3 positions

    def test_graph_based_filter_returns_correctly_with_single_element(self):
        # Arrange
        smr = {(2.5, 3.5)}
        min_pts = floor(0.02 * len(smr))
        expected = smr

        # Act
        result = RouteSkeleton.graph_based_filter(smr, 1, min_pts)
        
        # Assert
        assert result == expected

    def test_graph_based_filter_filters_outlier_correctly(self):
        # Arrange
        smr = set()

        for i in range(1, 101):
            smr.add((1 + 0.01 * i, 3.5))
        
        expected = deepcopy(smr)

        smr.add((23, 3.5)) #add cell more than radius prime distance from others  
        min_pts = floor(0.02 * len(smr)) #minimum of 2% of dataset size, this is an arbritrary value

        # Act
        result = RouteSkeleton.graph_based_filter(smr, 10, min_pts)
        # Assert
        assert (23, 3.5) not in result #check that outlier cell is correctly removed
        assert result == expected

    def test_graph_based_filter_returns_correctly_with_multiple_elements(self):
        # Arrange
        smr = set()

        for i in range(1, 101):
            smr.add((1 + 0.01 * i, 3.5))
        
        # Add two cell more than radius prime distance from others (should be enough to not be filtered out)
        smr.add((23, 3.5))        
        smr.add((23.1, 3.5))
        
        min_pts = floor(0.02 * len(smr))
        expected = smr
        # Act
        result = RouteSkeleton.graph_based_filter(smr, 20, min_pts)

        # Assert
        # Check that the two far cells are not removed
        assert (23, 3.5) in result
        assert (23.1, 3.5) in result
        assert result == expected

    def test_filter_sparse_points_returns_correctly_with_single_cell(self):
        # Arrange
        cmr = {(2, 3), (2,3.1)}
        expected = {(2, 3)}

        # Act
        result = RouteSkeleton.filter_sparse_points(cmr, 20)
        
        # Assert
        assert result == expected

    def test_filter_sparse_points_returns_correctly_with_two_cells(self):
        # Arrange
        cmr = {(2, 3),(22, 3)}

        # Act
        result = RouteSkeleton.filter_sparse_points(cmr, 20)
        result2 = RouteSkeleton.filter_sparse_points(cmr, 22)
        
        # Assert
        assert result == {(2, 3), (22, 3)}
        assert result2 == {(2, 3)}
        
        

    def test_filter_sparse_points_returns_correctly(self):
        # Arrange
        cmr = set()

        for i in range(1, 101):
            cmr.add((1 + 0.01 * i, 3.5))
        
        cmr.add((23, 3.5))

        # Act
        result = RouteSkeleton.filter_sparse_points(cmr, 20)

        # Assert
        assert (23, 3.5) in result
        assert len(result) == 2