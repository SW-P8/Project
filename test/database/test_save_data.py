from datetime import datetime
import pytest 
from geopy import distance

from DTC import gridsystem, trajectory
from database import save_data
from database.db import init_db

class TestLoadData():
    
    def _construct_gs(self) -> gridsystem.GridSystem:
        pc = trajectory.TrajectoryPointCloud()
        t = trajectory.Trajectory()

        # Add point to use initialization point
        t.add_point(1,0,datetime(2024, 1, 1, 1, 1, 1))
        for i in range(1, 5):
            # Shift points 5 meters north and east (should result in 5 points being 1 cell apart in both x and y)
            shifted_point = distance.distance(meters=i * 5).destination((t.points[0].latitude, t.points[0].longitude), 0)
            shifted_point = distance.distance(meters=i * 5).destination((shifted_point), 90)

            t.add_point(shifted_point.longitude, shifted_point.latitude, datetime(2024, 1, 1, 1, 1, 1 + i))
        pc.add_trajectory(t)
        gs = gridsystem.GridSystem(pc)
        gs.create_grid_system()

        gs.route_skeleton = {(2, 2), (7, 7)}
        gs.construct_safe_areas()        
        return gs 
    
    @pytest.fixture
    def test_save_data_with_fivepoint_grid_constructed_save_area(self):
        gs = self._construct_gs()
        db = init_db()
        
        try:
            save_data.save_data(gs,db)
            safe_areas = self._get_latest_min_coords_and_datapoints(db)
            expected_coords = []
            for (anc_x, anc_y, rad) in safe_areas:
                expected_coords.append((anc_x, anc_y, rad))
            return expected_coords

        except Exception:
            return None


    def _get_latest_min_coords_and_datapoints(self, db):
        conn = db.getconn()
        cursor = conn.cursor()
        safe_areas = []
        try:
            cursor.execute("SELECT model_id FROM DTC_model_min_coords ORDER BY model_id DESC LIMIT 1")
            result = cursor.fetchone()[0]
            print(result)
            if result:
                cursor.execute("SELECT anchor_x, anchor_y, radius FROM DTC_model_safe_areas WHERE model_id = %s", (result,))
                safe_areas = cursor.fetchall()
                return safe_areas
        except Exception as error:
            print("Error fetching latest min_coords:", error)
        finally:
            cursor.close()
        return None
    
    @pytest.fixture
    def test_insert_long_lat_returns_id(self):
        gs = self._construct_gs()
        db = init_db()
        min_long_lat = gs.pc.get_shifted_min()
        
        try:
            conn = db.getconn()
            cur = conn.cursor()
            id = save_data.insert_long_lat(min_long_lat[0], min_long_lat[1], conn, cur)
            return id
        except Exception:
            return None
        
    @pytest.fixture
    def test_insert_safe_areas_with_no_long_lat(self):
        gs = self._construct_gs()
        db = init_db()
        try:
            conn = db.getconn()
            cur = conn.cursor() 
            save_data.insert_safe_areas(1, gs.safe_areas, cur, conn)
            cur.execute("SELECT anchor_x, anchor_y, radius FROM DTC_model_safe_areas WHERE model_id = %s", (1,))
            safe_areas = cur.fetchall()
            return safe_areas
        except Exception:
            return "AssertionError"
        
    

    def test_save_data(self, test_save_data_with_fivepoint_grid_constructed_save_area, test_insert_safe_areas_with_no_long_lat, test_insert_long_lat_returns_id):
        actual_coords = [(7.0, 7.0, 2.8001428535179933), (2.0, 2.0, 2.800142853481284)]
        assert actual_coords == test_save_data_with_fivepoint_grid_constructed_save_area
        assert 1 == test_insert_long_lat_returns_id
        assert "AssertionError" == test_insert_safe_areas_with_no_long_lat
        

