from database import db, load_data
from database.taxi_data_handler import TaxiDataHandler
from DTC.clean_trajectory import CleanTrajectory
from DTC.gridsystem import GridSystem
from DTC.trajectory import TrajectoryPointCloud, Trajectory
import pytest


@pytest.fixture
def data():
    connection_pool = db.new_tdrive_db_pool()
    load_data.load_data_from_csv(connection_pool)
    data_handler = TaxiDataHandler(connection_pool)
    data = data_handler.read_n_records_inside_bbb(0, True)
    return data


@pytest.fixture
def model_data(data):
    testing_data = data[:1000]
    tid_of_existing_trajectory = 1
    trajectory = Trajectory()
    pc = TrajectoryPointCloud()
    for _, timestamp, longitude, latitude, tid in testing_data:
        if tid != tid_of_existing_trajectory:
            pc.add_trajectory(trajectory)
            trajectory = Trajectory()
            tid_of_existing_trajectory = tid
            trajectory.add_point(longitude, latitude, timestamp)
    pc.add_trajectory(trajectory)
    return pc


@pytest.fixture
def testing_data(data):
    testing_data = data[1000:1100]
    tid_of_existing_trajectory = 1
    trajectory = Trajectory()
    pc = TrajectoryPointCloud()
    for _, timestamp, longitude, latitude, tid in testing_data:
        if tid != tid_of_existing_trajectory:
            pc.add_trajectory(trajectory)
            trajectory = Trajectory()
            tid_of_existing_trajectory = tid
            trajectory.add_point(longitude, latitude, timestamp)
    pc.add_trajectory(trajectory)
    return pc.trajectories


@pytest.fixture
def grid_system():
    grid_system = GridSystem()
    

@pytest.fixture
def cleaner(grid_system):
    cleaner = CleanTrajectory(
        grid_system.safe_areas, grid_system.route_skeleton, grid_system.initialization_point)
    return cleaner


def test_safe_areas_can_be_updated():
    pass

