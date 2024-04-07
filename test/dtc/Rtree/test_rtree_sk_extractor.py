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
