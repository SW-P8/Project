import pytest
from database import db, load_data, taxi_data_handler
from DTC import dtc_executor, gridsystem
from DTC.route_skeleton import RouteSkeleton
from DTC.construct_safe_area import ConstructSafeArea
import DTC.json_read_write as json_read_write

class TestCheapBenchmark:
    @classmethod
    def setup_class(cls):
        cls.grid_system = None
        cls.point_cloud = None
        cls.limit = 1000
        cls.n_points = 100000
        cls.conn = None
        cls.handler = None
        cls.executor = None

    @pytest.mark.bm_cheap
    def test_db_setup(self):
        self.__class__.conn = db.new_tdrive_db_pool()
        load_data.load_data_from_csv(self.__class__.conn, self.__class__.limit)
        self.__class__.handler = taxi_data_handler.TaxiDataHandler(self.__class__.conn)
        self.__class__.executor = dtc_executor.DTCExecutor()
        assert True

    @pytest.mark.bm_cheap
    def test_point_cloud(self, benchmark):
        point_cloud = benchmark.pedantic(self.__class__.executor.create_point_cloud_with_n_points, kwargs={'n':self.__class__.n_points, 'city': True}, rounds=1, iterations=1, warmup_rounds=0)
        self.__class__.point_cloud = point_cloud
        self.__class__.grid_system = gridsystem.GridSystem(point_cloud)
        assert point_cloud is not None
    
    @pytest.mark.bm_cheap
    def test_build_grid_system(self, benchmark):
        benchmark.pedantic(self.__class__.grid_system.create_grid_system, rounds=1, iterations=1, warmup_rounds=0)
        json_read_write.write_grid_to_json("test_grid.json", self.__class__.grid_system.grid)
        assert self.__class__.grid_system != None
    
    @pytest.mark.bm_cheap
    def test_extract_main_route(self, benchmark):
        benchmark.pedantic(self.__class__.grid_system.extract_main_route, rounds=1, iterations=1, warmup_rounds=0)
        json_read_write.write_set_of_tuples_to_json("test_mr.json", self.__class__.grid_system.main_route)
        assert self.__class__.grid_system != None
    
    @pytest.mark.bm_cheap
    def test_extract_route_skeleton(self, benchmark):
        main_route = json_read_write.read_set_of_tuples_from_json("test_mr.json")
        route_skeleton = benchmark.pedantic(RouteSkeleton.extract_route_skeleton, kwargs={'main_route': main_route, 'smooth_radius': 25, 'filtering_list_radius': 20, 'distance_interval': 20}, rounds=1, iterations=1, warmup_rounds=0)
        json_read_write.write_set_of_tuples_to_json("test_rsk.json", route_skeleton)
        assert route_skeleton != None

    @pytest.mark.bm_cheap
    def test_construct_safe_area(self, benchmark):
        route_skeleton = json_read_write.read_set_of_tuples_from_json("test_rsk.json")
        grid = json_read_write.read_grid_from_json("test_grid.json")

        safe_areas = benchmark.pedantic(ConstructSafeArea.construct_safe_areas, kwargs={'route_skeleton': route_skeleton, 'grid': grid, 'decrease_factor': 0.01, 'initialization_point': (0,0)}, rounds=1, iterations=1, warmup_rounds=0)
        
        json_read_write.write_safe_areas_to_json("test_sa.json", safe_areas)
