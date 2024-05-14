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
        cls.limit = 100000
        cls.n_points = 100000000
        cls.conn = None
        cls.handler = None
        cls.executor = None
        cls.pc_file = "AllcityPC.json"
        cls.grid_file = "AllcityGrid.json"
        cls.mr_file = "AllcityMR.json"
        cls.rsk_file = "AllcityRSK.json"
        cls.sa_file = "AllcitySA.json"
        cls.city_bb = True
        cls.smooth_radius = 25
        cls.filter_radius = 20
        cls.sample_radius = 20
        cls.decrease_factor = 0.01
        cls.find_relaxed_nn = True
        cls.should_write_to_json = False
        cls.with_time = True

    @pytest.mark.bm_cheap
    def test_db_setup(self):
        self.__class__.conn = db.new_tdrive_db_pool()
        load_data.load_data_from_csv(self.__class__.conn, self.__class__.limit)
        self.__class__.handler = taxi_data_handler.TaxiDataHandler(self.__class__.conn)
        self.__class__.executor = dtc_executor.DTCExecutor()
        assert True

    @pytest.mark.bm_cheap
    def test_point_cloud(self, benchmark):
        point_cloud = benchmark.pedantic(self.__class__.executor.create_point_cloud_with_n_points, kwargs={'n':self.__class__.n_points, 'city': self.city_bb, 'with_time': self.with_time}, rounds=1, iterations=1, warmup_rounds=0)
        if self.should_write_to_json:
            json_read_write.write_point_cloud_to_json(self.pc_file, point_cloud)
        assert point_cloud is not None
    
    @pytest.mark.bm_cheap
    def test_build_grid_system(self, benchmark):
        point_cloud = json_read_write.read_point_cloud_from_json(self.pc_file)
        self.__class__.grid_system = gridsystem.GridSystem(point_cloud)
        benchmark.pedantic(self.__class__.grid_system.create_grid_system, rounds=1, iterations=1, warmup_rounds=0)
        if self.should_write_to_json:
            json_read_write.write_grid_to_json(self.grid_file, self.__class__.grid_system.grid)
        assert self.__class__.grid_system != None
    
    @pytest.mark.bm_cheap
    def test_extract_main_route(self, benchmark):
        benchmark.pedantic(self.__class__.grid_system.extract_main_route, rounds=1, iterations=1, warmup_rounds=0)
        if self.should_write_to_json:
            json_read_write.write_set_of_tuples_to_json(self.mr_file, self.__class__.grid_system.main_route)
        assert self.__class__.grid_system != None
    
    @pytest.mark.bm_cheap
    def test_extract_route_skeleton(self, benchmark):
        main_route = json_read_write.read_set_of_tuples_from_json(self.mr_file)
        route_skeleton = benchmark.pedantic(RouteSkeleton.extract_route_skeleton, kwargs={'main_route': main_route, 'smooth_radius': self.smooth_radius, 'filtering_list_radius': self.filter_radius, 'distance_interval': self.sample_radius}, rounds=1, iterations=1, warmup_rounds=0)
        if self.should_write_to_json:
            json_read_write.write_set_of_tuples_to_json(self.rsk_file, route_skeleton)
        assert route_skeleton != None

    @pytest.mark.bm_cheap
    def test_construct_safe_area(self, benchmark):
        route_skeleton = json_read_write.read_set_of_tuples_from_json(self.rsk_file)
        grid = json_read_write.read_grid_from_json(self.grid_file)

        safe_areas = benchmark.pedantic(ConstructSafeArea.construct_safe_areas, kwargs={'route_skeleton': route_skeleton, 'grid': grid, 'find_relaxed_nn': self.find_relaxed_nn}, rounds=1, iterations=1, warmup_rounds=0)
        
        if self.should_write_to_json:
            json_read_write.write_safe_areas_to_json(self.sa_file, safe_areas)
