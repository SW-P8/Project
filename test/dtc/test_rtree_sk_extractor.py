from DTC.rtree_sk_extractor import RTreeSkeletonExtractor
from rtree.index import Index

class TestRTreeSKExtractor:
    def test_smooth_main_route_returns_correctly_with_single_element(self):
        mr = Index()
        mr.insert(1, [3, 3, 3, 3])

        expected_ids = [1]
        expected_point = [3.5, 3.5, 3.5, 3.5]

        actual_smr = RTreeSkeletonExtractor.smooth_main_route(mr)
        actual_ids = list(actual_smr.intersection((float('-inf'), float('-inf'), float('inf'), float('inf'))))
        actual_point = actual_smr.get_bounds(actual_ids[0])

        # Should simply contain the center of the single cell
        assert actual_ids == expected_ids
        assert actual_point == expected_point

    def test_smooth_main_route_returns_correctly_with_two_elements(self):
        mr = Index()
        mr.insert(1, [3, 3, 3, 3])
        mr.insert(2, [27, 3, 27, 3])

        expected_ids = [1, 2]
        expected_point1 = [15.5, 3.5, 15.5, 3.5]
        expected_point2 = [15.5, 3.5, 15.5, 3.5]

        actual_smr = RTreeSkeletonExtractor.smooth_main_route(mr)
        hits = list(actual_smr.intersection((float('-inf'), float('-inf'), float('inf'), float('inf')), objects=True))
        points = [(item.object, item.bbox) for item in hits]
        _, actual_point1 = points[0]
        _, actual_point2 = points[1]

        # Should only contain the avg position of the two cells centers
        #assert actual_ids == expected_ids
        assert actual_point1 == expected_point1
        assert actual_point2 == expected_point2

        # expected_ids = [1, 2]
        # expected_point1 = [3.5, 3.5, 3.5, 3.5]
        # expected_point2 = [27.5, 3.5, 27.5, 3.5]

        # actual_smr = RTreeSkeletonExtractor.smooth_main_route(mr, 20)
        # actual_ids = list(actual_smr.intersection((float('-inf'), float('-inf'), float('inf'), float('inf'))))
        # actual_point1 = actual_smr.get_bounds(actual_ids[0])
        # actual_point2 = actual_smr.get_bounds(actual_ids[1])

        # # Should contain the centers of the two cells as they are too far apart
        # assert actual_ids == expected_ids
        # assert actual_point1 == expected_point1
        # assert actual_point2 == expected_point2