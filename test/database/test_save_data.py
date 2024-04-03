from datetime import datetime
import pytest 
from geopy import distance

from DTC import gridsystem, trajectory
from database import save_data
from database.db import init_db

@pytest.fixture
def test_save_data_with_fivepoint_grid_constructed_save_area():
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
    db = init_db()
    print(gs.safe_areas)
    print(gs.pc.get_shifted_min())
    try:
        save_data.save_data(gs,db)
        safe_areas = get_latest_min_coords_and_datapoints(db)
        expected_coords = []
        actual_coords = []
        print(safe_areas)
        print(gs.safe_areas)
        for (anc_x, anc_y, rad) in safe_areas:
            expected_coords.append((anc_x, anc_y, rad))
        for (x, y), radi in gs.safe_areas.items():
            actual_coords.append((x, y, radi))
        return(actual_coords, expected_coords)
            
    except Exception as e:
        print("test_failed", e)
        return None


def get_latest_min_coords_and_datapoints(db):
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

def test_save_data(test_save_data_with_fivepoint_grid_constructed_save_area):
    result = test_save_data_with_fivepoint_grid_constructed_save_area
    assert result[0] == result[1]