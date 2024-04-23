import pytest

from database import db, load_data, taxi_data_handler
from DTC import dtc_executor, gridsystem
from DTC.route_skeleton import RouteSkeleton
import json

class TestCheapBenchmark:
    @classmethod
    def setup_class(cls):
        cls.grid_system = None
        cls.point_cloud = None
        cls.limit = 100000
        cls.n_points = 100000000
        cls.conn = None
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
#        point_cloud = benchmark.pedantic(self.__class__.executor.create_point_cloud_with_n_points, kwargs={'n':self.__class__.n_points}, rounds=1, iterations=1, warmup_rounds=0)
#        self.__class__.point_cloud = point_cloud
#        self.__class__.grid_system = gridsystem.GridSystem(point_cloud)
#        assert point_cloud is not None
#    
#    @pytest.mark.bm_cheap
#    def test_build_grid_system(self, benchmark):
#        def obj_dict(obj):
#            return obj.__dict__
#        
#        benchmark.pedantic(self.__class__.grid_system.create_grid_system, rounds=1, iterations=1, warmup_rounds=0)
#        #with open("AllGrid.json", "w") as outfile: 
#        #    json.dump(str(self.__class__.grid_system.initialization_point) ,outfile)
#        #    json.dump({str(k): v for k, v in self.__class__.grid_system.grid.items()}, outfile, default=obj_dict, indent=4)
#        assert self.__class__.grid_system != None
#    
#    @pytest.mark.bm_cheap
#    def test_extract_main_route(self, benchmark):
#        benchmark.pedantic(self.__class__.grid_system.extract_main_route, rounds=1, iterations=1, warmup_rounds=0)
#        #with open("AllMR.json", "w") as outfile: 
#        #    json.dump([str(v) for v in self.__class__.grid_system.main_route], outfile, indent=4)
#        assert self.__class__.grid_system != None
#    
    @pytest.mark.bm_cheap
    def test_extract_route_skeleton(self, benchmark):
        with open("100kMR.json", "r") as infile:
            data = json.load(infile)
        print(len(data))
        main_route = {eval(v) for v in data}
        print(len(main_route))
        route_skeleton = benchmark.pedantic(RouteSkeleton.extract_route_skeleton, kwargs={'main_route': main_route, 'smooth_radius': 25, 'filtering_list_radius': 20, 'distance_interval': 20}, rounds=1, iterations=1, warmup_rounds=0)
        with open("100kRSK.json", "w") as outfile: 
            json.dump([str(v) for v in route_skeleton], outfile, indent=4)
        assert route_skeleton != None

#    @pytest.mark.bm_cheap
#    def test_construct_safe_area(self, benchmark):
#        benchmark.pedantic(self.__class__.grid_system.construct_safe_areas, rounds=1, iterations=1, warmup_rounds=0)
#        assert self.__class__.grid_system != None
