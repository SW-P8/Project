import pytest

from database import db, load_data, taxi_data_handler
from DTC import dtc_executor, gridsystem
from DTC.route_skeleton import RouteSkeleton
from DTC.construct_safe_area import ConstructSafeArea
import json

class TestCheapBenchmark:
    @classmethod
    def setup_class(cls):
        cls.grid_system = None
        cls.point_cloud = None
#        cls.limit = 100000
#        cls.n_points = 1000000000
#        cls.conn = None
#        cls.handler = None
#        cls.executor = None
#
#    @pytest.mark.bm_cheap
#    def test_db_setup(self):
#        self.__class__.conn = db.new_tdrive_db_pool()
#        load_data.load_data_from_csv(self.__class__.conn, self.__class__.limit)
#        self.__class__.handler = taxi_data_handler.TaxiDataHandler(self.__class__.conn)
#        self.__class__.executor = dtc_executor.DTCExecutor()
#        assert True
#
#    @pytest.mark.bm_cheap
#    def test_point_cloud(self, benchmark):
#        point_cloud = benchmark.pedantic(self.__class__.executor.create_point_cloud_with_n_points, kwargs={'n':self.__class__.n_points, 'city': True}, rounds=1, iterations=1, warmup_rounds=0)
#        self.__class__.point_cloud = point_cloud
#        self.__class__.grid_system = gridsystem.GridSystem(point_cloud)
#        assert point_cloud is not None
#    
#    @pytest.mark.bm_cheap
#    def test_build_grid_system(self, benchmark):
#        benchmark.pedantic(self.__class__.grid_system.create_grid_system, rounds=1, iterations=1, warmup_rounds=0)
#        with open("AllcityGrid.json", "w") as outfile: 
#            json.dump(str(self.__class__.grid_system.initialization_point) ,outfile)
#            json.dump({str(k): v for k, v in self.__class__.grid_system.grid.items()}, outfile, default=obj_dict, indent=4)
#        assert self.__class__.grid_system != None
#    
#    @pytest.mark.bm_cheap
#    def test_extract_main_route(self, benchmark):
#        benchmark.pedantic(self.__class__.grid_system.extract_main_route, rounds=1, iterations=1, warmup_rounds=0)
#        with open("AllcityMR.json", "w") as outfile: 
#            json.dump([str(v) for v in self.__class__.grid_system.main_route], outfile, indent=4)
#        assert self.__class__.grid_system != None
#    
#    @pytest.mark.bm_cheap
#    def test_extract_route_skeleton(self, benchmark):
#        with open("5milcityMR.json", "r") as infile:
#            data = json.load(infile)
#        main_route = {eval(v) for v in data}
#        print("Main route: " + str(len(main_route)))
#        route_skeleton = benchmark.pedantic(RouteSkeleton.extract_route_skeleton, kwargs={'main_route': main_route, 'smooth_radius': 25, 'filtering_list_radius': 20, 'distance_interval': 20}, rounds=1, iterations=1, warmup_rounds=0)
#        assert route_skeleton != set()
#        print("Route skeleton: " + str(len(route_skeleton)))
#        with open("5milcityRSK.json", "w") as outfile: 
#            json.dump([str(v) for v in route_skeleton], outfile, indent=4)
#        assert route_skeleton != None

    @pytest.mark.bm_cheap
    def test_construct_safe_area(self, benchmark):
        with open("AllRSK.json", "r") as rskinfile:
            rsk_data = json.load(rskinfile)
        route_skeleton = {eval(v) for v in rsk_data}

        with open('AllGrid.json', 'r') as gridfile:
            grid_data = json.load(gridfile)

        grid = dict()
        for key, value in grid_data.items():
            key_tuple = eval(key)
            value_tuples = [tuple(sublist) for sublist in value]
            grid[key_tuple] = value_tuples

        safe_areas = benchmark.pedantic(ConstructSafeArea.construct_safe_areas, kwargs={'route_skeleton': route_skeleton, 'grid': grid, 'decrease_factor': 0.01, 'initialization_point': (0,0)}, rounds=1, iterations=1, warmup_rounds=0)
        
        with open("AllSA.json", "w") as outfile: 
            json.dump({str(k): [v.radius, v.cardinality] for k, v in safe_areas.items()}, outfile, indent=4) 
