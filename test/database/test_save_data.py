from datetime import datetime
import pytest 
from geopy import distance

from DTC import gridsystem, trajectory
from database import save_data
from database.db import init_db


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
    except Exception as e:
        print("test_failed", e)

    
test_save_data_with_fivepoint_grid_constructed_save_area()