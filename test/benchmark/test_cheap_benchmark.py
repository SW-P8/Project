import pytest

from database import db, load_data, taxi_data_handler
from DTC import dtc_executor, gridsystem

class TestCheapBenchmark:
    @classmethod
    def setup_class(cls):
        cls.grid_system = None
        cls.point_cloud = None
        cls.limit = 1000
        cls.n_points = 1000000
        cls.conn = None
        cls.handler = None
        cls.executor = None

    @pytest.mark.bm_cheap
    def test_db_setup(self):
        self.__class__.conn = db.init_db()
        load_data.load_data_from_csv(self.__class__.conn, self.__class__.limit)
        self.__class__.handler = taxi_data_handler.TaxiDataHandler(self.__class__.conn)
        self.__class__.executor = dtc_executor.DTCExecutor()
        assert True

    @pytest.mark.bm_cheap
    def test_point_cloud(self, benchmark):
        point_cloud = benchmark.pedantic(self.__class__.executor.create_point_cloud_with_n_points, kwargs={'n':self.__class__.n_points}, rounds=1, iterations=1, warmup_rounds=0)
        self.__class__.point_cloud = point_cloud
        self.__class__.grid_system = gridsystem.GridSystem(point_cloud)
        assert point_cloud is not None
    
    @pytest.mark.bm_cheap
    def test_build_grid_system(self, benchmark):
        benchmark.pedantic(self.__class__.grid_system.create_grid_system, rounds=1, iterations=1, warmup_rounds=0)
        assert self.__class__.grid_system != None
#    
    @pytest.mark.bm_cheap
    def test_extract_main_route(self, benchmark):
        benchmark.pedantic(self.__class__.grid_system.extract_main_route, rounds=1, iterations=1, warmup_rounds=0)
        print(len(self.__class__.grid_system.main_route))

        assert self.__class__.grid_system != None
    
#    @pytest.mark.bm_cheap
#    def test_extract_route_skeleton(self, benchmark):
#        benchmark.pedantic(self.__class__.grid_system.extract_route_skeleton, rounds=1, iterations=1, warmup_rounds=0)
#        assert self.__class__.grid_system != None

#    @pytest.mark.bm_cheap
#    def test_construct_safe_area(self, benchmark):
#        benchmark.pedantic(self.__class__.grid_system.construct_safe_areas, rounds=1, iterations=1, warmup_rounds=0)
#        assert self.__class__.grid_system != None
