import pytest

from database import db, load_data, taxi_data_handler
from DTC import dtc_executor, gridsystem

@pytest.mark.skip(reason="Benchmarking should not run on normal test runs")
class TestMidBenchmark:
    @classmethod
    def setup_class(cls):
        cls.grid_system = None
        cls.point_cloud = None
        cls.limit = 4000
        cls.n_points = 5000000
        cls.conn = db.init_db()
        load_data.load_data_from_csv(cls.conn, cls.limit)
        cls.handler = taxi_data_handler.TaxiDataHandler(cls.conn)
        cls.executor = dtc_executor.DTCExecutor()

    @pytest.mark.bm_mid
    def test_point_cloud(self, benchmark):
        point_cloud = benchmark.pedantic(self.__class__.executor.create_point_cloud_with_n_points, kwargs={'n':self.__class__.n_points}, rounds=4, iterations=1, warmup_rounds=0)
        self.__class__.point_cloud = point_cloud
        self.__class__.grid_system = gridsystem.GridSystem(point_cloud)
        assert point_cloud is not None
    
    @pytest.mark.bm_mid
    def test_build_grid_system(self, benchmark):
        benchmark.pedantic(self.__class__.grid_system.create_grid_system, rounds=5, iterations=3, warmup_rounds=0)
        assert self.__class__.grid_system != None
    
    @pytest.mark.bm_mid
    def test_extract_main_route(self, benchmark):
        benchmark.pedantic(self.__class__.grid_system.extract_main_route, rounds=5, iterations=3, warmup_rounds=0)
        assert self.__class__.grid_system != None
    
    @pytest.mark.bm_mid
    def test_extract_route_skeleton(self, benchmark):
        benchmark.pedantic(self.__class__.grid_system.extract_route_skeleton, rounds=5, iterations=3, warmup_rounds=0)
        assert self.__class__.grid_system != None

    @pytest.mark.bm_mid
    def test_construct_safe_area(self, benchmark):
        benchmark.pedantic(self.__class__.grid_system.construct_safe_areas, rounds=5, iterations=3, warmup_rounds=0)
        assert self.__class__.grid_system != None