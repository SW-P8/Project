from DTC.Rtree.rtree_sk_extractor import RTreeSkeletonExtractor
from rtree.index import Index

class TestRTreeSKExtractor:
    def test_smooth_main_route_returns_correctly_with_single_element(self):
        mr = Index()
        mr.insert(1, [3, 3, 3, 3])

        expected_point = [3.5, 3.5, 3.5, 3.5]

        actual_smr = RTreeSkeletonExtractor.smooth_main_route(mr)
        hits = list(actual_smr.intersection((float('-inf'), float('-inf'), float('inf'), float('inf')), objects=True))
        points = [(item.object, item.bbox) for item in hits]
        _, actual_point = points[0]

        # Should simply contain the center of the single cell
        assert actual_point == expected_point
        assert len(points) == 1


    def test_smooth_main_route_returns_correctly_with_two_elements(self):
        mr = Index()
        mr.insert(1, [3, 3, 3, 3])
        mr.insert(2, [27, 3, 27, 3])

        expected_point1 = [15.5, 3.5, 15.5, 3.5]

        actual_smr = RTreeSkeletonExtractor.smooth_main_route(mr)
        hits = list(actual_smr.intersection((float('-inf'), float('-inf'), float('inf'), float('inf')), objects=True))
        points = [(item.object, item.bbox) for item in hits]
        _, actual_point1 = points[0]

        # Should only contain the avg position of the two cells centers
        #assert actual_ids == expected_ids
        assert actual_point1 == expected_point1
        assert len(points) == 1

        expected_point1 = [3.5, 3.5, 3.5, 3.5]
        expected_point2 = [27.5, 3.5, 27.5, 3.5]

        actual_smr = RTreeSkeletonExtractor.smooth_main_route(mr, radius=20)
        hits = list(actual_smr.intersection((float('-inf'), float('-inf'), float('inf'), float('inf')), objects=True))
        points = [(item.object, item.bbox) for item in hits]
        _, actual_point1 = points[0]
        _, actual_point2 = points[1]

        # # Should contain the centers of the two cells as they are too far apart
        assert actual_point1 == expected_point1
        assert actual_point2 == expected_point2
        assert len(points) == 2

    
    # Points in grid are not used here as operations are made only on main route
    def test_smooth_main_route_returns_correctly_with_multiple_elements(self):
        mr = Index()
        mr.insert(1, [2, 3, 2, 3])
        mr.insert(2, [27, 3, 27, 3])
        mr.insert(3, [32, 3, 32, 3])

        expected_point1 = [15, 3.5, 15, 3.5]
        expected_point2 = [(2.5 + 27.5 + 32.5)/3, 3.5, (2.5 + 27.5 + 32.5)/3, 3.5]
        expected_point3 = [30, 3.5, 30, 3.5]

        actual_smr = RTreeSkeletonExtractor.smooth_main_route(mr)
        hits = list(actual_smr.intersection((float('-inf'), float('-inf'), float('inf'), float('inf')), objects=True))
        points = [(item.object, item.bbox) for item in hits]
        _, actual_point1 = points[0]
        _, actual_point2 = points[1]
        _, actual_point3 = points[2]

        # Should only contain the avg position of the two cells centers
        assert actual_point1 == expected_point1
        assert actual_point2 == expected_point2
        assert actual_point3 == expected_point3
        assert len(points) == 3

    def test_filter_outliers_in_main_route_returns_correctly_with_single_element(self):
        smr = Index()
        smr.insert(1, [2.5, 3.5, 2.5, 3.5])

        expected_point = [2.5, 3.5, 2.5, 3.5]

        actual_cmr = RTreeSkeletonExtractor.filter_outliers_in_main_route(smr)
        hits = list(actual_cmr.intersection((float('-inf'), float('-inf'), float('inf'), float('inf')), objects=True))
        points = [(item.object, item.bbox) for item in hits]
        _, actual_point = points[0]

        # Should simply contain the center of the single cell
        assert actual_point == expected_point
        assert len(points) == 1

    def test_filter_outliers_in_main_route_filters_outlier_correctly(self):
        smr = Index()
        for i in range(1, 101):
            smr.insert(i, [1 + 0.01 * i, 3.5, 1 + 0.01 * i, 3.5])
        
        # Add cell more than radius prime distance from others
        smr.insert(101, [23, 3.5, 23, 3.5])
        actual_cmr = RTreeSkeletonExtractor.filter_outliers_in_main_route(smr)
        hits = list(actual_cmr.intersection((float('-inf'), float('-inf'), float('inf'), float('inf')), objects=True))
        points = [(item.object, item.bbox) for item in hits]
        points_bbox = [bbox for _, bbox in points]

        # Check that outlier cell is correctly removed
        assert [23, 3.5, 23, 3.5] not in points_bbox
        assert len(points) == 100

    def test_filter_outliers_in_main_route_returns_correctly_with_multiple_elements(self):
        smr = Index()
        for i in range(1, 101):
            smr.insert(i, [1 + 0.01 * i, 3.5, 1 + 0.01 * i, 3.5])
        
        # Add two cells more than radius prime distance from others
        smr.insert(101, [23, 3.5, 23, 3.5])
        smr.insert(102, [23.1, 3.5, 23.1, 3.5])
        actual_cmr = RTreeSkeletonExtractor.filter_outliers_in_main_route(smr)
        hits = list(actual_cmr.intersection((float('-inf'), float('-inf'), float('inf'), float('inf')), objects=True))
        points = [(item.object, item.bbox) for item in hits]
        points_bbox = [bbox for _, bbox in points]

        # Check that outlier cell is correctly removed
        assert [23, 3.5, 23, 3.5] in points_bbox
        assert [23.1, 3.5, 23.1, 3.5] in points_bbox
        assert len(points) == 102

    def test_sample_main_route_returns_correctly_with_single_cell(self):
        cmr = Index()
        cmr.insert(1, [2, 3, 2, 3])
        rs = RTreeSkeletonExtractor.sample_main_route(cmr)
        assert rs == set()

    def test_sample_main_route_returns_correctly_with_two_cells(self):
        cmr = Index()
        cmr.insert(1, [2, 3, 2, 3])
        cmr.insert(2, [22, 3, 22, 3])
        rs1 = RTreeSkeletonExtractor.sample_main_route(cmr)
        assert rs1 == {(2, 3), (22, 3)}

        rs2 = RTreeSkeletonExtractor.sample_main_route(cmr, 19)
        assert rs2 == set()

    def test_sample_main_route_returns_correctly(self):
        cmr = Index()
        expected_rs = set()
        for i in range(1, 101):
            cmr.insert(i, [1 + 0.01 * i, 3.5, 1 + 0.01 * i, 3.5])
            expected_rs.add((1 + 0.01 * i, 3.5))
        
        # Add cell a large distance from others
        cmr.insert(101, [23, 3.5, 23, 3.5])
        actual_rs = RTreeSkeletonExtractor.sample_main_route(cmr)

        # Check that outlier cell is correctly removed
        assert (23, 3.5) not in actual_rs
        assert actual_rs == expected_rs

    def test_extract_route_skeleton_returns_correctly_with_single_cell(self):
        main_route = Index()
        main_route.insert(1, [2, 3, 2, 3])
        rs = RTreeSkeletonExtractor.extract_route_skeleton(main_route)
        assert rs == set()

    def test_extract_route_skeleton_returns_correctly_with_two_cells(self):
        main_route = Index()
        main_route.insert(1, [2, 3, 2, 3])
        main_route.insert(2, [12, 3, 12 ,3])
        rs = RTreeSkeletonExtractor.extract_route_skeleton(main_route)
        assert rs == set()

    def test_extract_route_skeleton_returns_correctly_with_three_cells(self):
        main_route = Index()
        main_route.insert(1, [2, 3, 2, 3])
        main_route.insert(2, [27, 3, 27 ,3])
        main_route.insert(3, [32, 3, 32, 3])
        rs = RTreeSkeletonExtractor.extract_route_skeleton(main_route)
        assert rs == {(15, 3.5), ((2.5 + 27.5 + 32.5)/3, 3.5), (30, 3.5)}

    def test_extract_route_skeleton_returns_correctly_with_many_cells(self):
        main_route = Index()
        for i in range(0, 27):
            main_route.insert(i, [-24 + 1 * i, 3, -24 + 1 * i, 3])

        # Add cell more than radius distance from others to not have it be smoothed and therefore later filtered out
        main_route.insert(27, [28, 3, 28, 3])

        rs = RTreeSkeletonExtractor.extract_route_skeleton(main_route)

        assert (28.5, 3.5) not in rs
        assert rs != set()