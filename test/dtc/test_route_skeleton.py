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

    def test_sample_contracted_main_route_returns_correctly_with_single_cell(self):
        cmr = {(2, 3): {(2, 3)}}
        rs = RouteSkeleton.sample_contracted_main_route(cmr, 20)
        
        assert rs == set()

    def test_sample_contracted_main_route_returns_correctly_with_two_cells(self):
        cmr = {(2, 3): {(2, 3)}, (22, 3): {(22, 3)}}
        rs1 = RouteSkeleton.sample_contracted_main_route(cmr, 20)
        
        assert rs1 == {(2, 3), (22, 3)}

        rs2 = RouteSkeleton.sample_contracted_main_route(cmr, 19)
        
        assert rs2 == set()

    def test_sample_contracted_main_route_returns_correctly(self):
        cmr = defaultdict(set)

        for i in range(1, 101):
            cmr[(int(1 + 0.01 * i), 3)].add((1 + 0.01 * i, 3.5))
        
        # Add cell a large distance from others
        cmr[(23, 3)].add((23, 3.5))
        rs = RouteSkeleton.sample_contracted_main_route(cmr, 20)

        # Check that outlier cell is correctly removed
        assert (23, 3.5) not in rs
