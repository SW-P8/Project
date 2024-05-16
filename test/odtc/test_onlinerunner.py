import pytest
from onlinedtc.onlinerunner import RunCleaning
from DTC.gridsystem import GridSystem
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
