import pytest
from onlinedtc.onlinerunner import RunCleaning
from DTC.gridsystem import GridSystem
from DTC.route_skeleton import RouteSkeleton
from DTC.trajectory import TrajectoryPointCloud, Trajectory


@pytest.fixture
def trajectory():
    t = Trajectory()
    for i in range(10):
        t.add_point(i, i)
    return t


@pytest.fixture
def point_cloud(trajectory):
    pc = TrajectoryPointCloud()
    for _ in range(10):
        pc.add_trajectory(trajectory)
    return pc


def test_init_no_grid_raises_error(point_cloud):
    # Arrange
    grid_system = GridSystem(point_cloud)
    smooth_main_route = set()

    # Act + Assert
    with pytest.raises(AttributeError):
        RunCleaning(grid_system, smooth_main_route)


@pytest.fixture
def grid_system(point_cloud):
    gs = GridSystem(point_cloud)
    rs = RouteSkeleton()
    gs.create_grid_system()
    gs.extract_main_route()
    smr = rs.smooth_main_route(gs.main_route)
    fmr = rs.graph_based_filter(smr, )
    return 
