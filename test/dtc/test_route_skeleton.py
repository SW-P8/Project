from DTC.route_skeleton import RouteSkeleton
from collections import defaultdict

class TestRouteSkeleton():
    def test_smooth_main_route_returns_correctly_with_single_element(self):
        main_route = {(3, 3)}
        smr = RouteSkeleton.smooth_main_route(main_route, 25)

        # Should simply contain the center of the single cell
        assert smr == {(3, 3): {(3.5, 3.5)}}

    def test_smooth_main_route_returns_correctly_with_two_elements(self):
        main_route = {(3, 3), (27, 3)}
        smr1 = RouteSkeleton.smooth_main_route(main_route, 25)

        # Should only contain the avg position of the two cells centers
        assert smr1 == {(15, 3): {(15.5, 3.5)}}

        smr2 = RouteSkeleton.smooth_main_route(main_route, 20)

        # Should contain the centers of the two cells as they are too far apart
        assert smr2 == {(3, 3): {(3.5, 3.5)}, (27, 3): {(27.5, 3.5)}}

    def test_smooth_main_route_returns_correctly_with_multiple_elements(self):
        main_route = {(2, 3), (27, 3), (32, 3)}
        smr = RouteSkeleton.smooth_main_route(main_route, 25)

        # Should only contain 3 positions
        assert smr == {(15, 3): {(15, 3.5)}, (20, 3): {(20.83, 3.5)}, (30, 3): {(30, 3.5)}}

    def test_filter_outliers_in_main_route_returns_correctly_with_single_element(self):
        smr = {(2, 3): {(2.5, 3.5)}}
        cmr = RouteSkeleton.filter_outliers_in_main_route(smr, 1, 20)
        
        assert cmr == {(2, 3): {(2.5, 3.5)}}

    def test_filter_outliers_in_main_route_filters_outlier_correctly(self):
        smr = defaultdict(set)

        for i in range(1, 101):
            smr[(int(1 + 0.01 * i), 3)].add((1 + 0.01 * i, 3.5))
        
        # Add cell more than radius prime distance from others
        smr[(23, 3)].add((23, 3.5))        
        cmr = RouteSkeleton.filter_outliers_in_main_route(smr, 101, 20)

        # Check that outlier cell is correctly removed
        assert (23, 3) not in cmr.keys()
        assert cmr[(23, 3)] == set()

    def test_filter_outliers_in_main_route_returns_correctly_with_multiple_elements(self):
        smr = defaultdict(set)

        for i in range(1, 101):
            smr[(int(1 + 0.01 * i), 3)].add((1 + 0.01 * i, 3.5))
        
        # Add two cell more than radius prime distance from others (should be enough to not be filtered out)
        smr[(23, 3)].add((23, 3.5))        
        smr[(23, 3)].add((23.1, 3.5))        
        cmr = RouteSkeleton.filter_outliers_in_main_route(smr, 102, 20)

        # Check that the two far cells are not removed
        assert (23, 3) in cmr.keys()
        assert cmr[(23, 3)] == {(23, 3.5), (23.1, 3.5)}

    def test_sample_main_route_returns_correctly_with_single_cell(self):
        cmr = {(2, 3): {(2, 3)}}
        rs = RouteSkeleton.sample_main_route(cmr, 20)
        
        assert rs == set()

    def test_sample_main_route_returns_correctly_with_two_cells(self):
        cmr = {(2, 3): {(2, 3)}, (22, 3): {(22, 3)}}
        rs1 = RouteSkeleton.sample_main_route(cmr, 20)
        
        assert rs1 == {(2, 3), (22, 3)}

        rs2 = RouteSkeleton.sample_main_route(cmr, 19)
        
        assert rs2 == set()

    def test_sample_main_route_returns_correctly(self):
        cmr = defaultdict(set)

        for i in range(1, 101):
            cmr[(int(1 + 0.01 * i), 3)].add((1 + 0.01 * i, 3.5))
        
        # Add cell a large distance from others
        cmr[(23, 3)].add((23, 3.5))
        rs = RouteSkeleton.sample_main_route(cmr, 20)

        # Check that outlier cell is correctly removed
        assert (23, 3.5) not in rs
 
