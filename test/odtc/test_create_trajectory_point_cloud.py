from onlinedtc.runner import *
from DTC.trajectory import Trajectory, TrajectoryPointCloud

def test_create_trajectory_point_cloud():
    # Arrange
    trajectory = Trajectory()
    for i in range(20):
        trajectory.add_point((1 + 0.1 * i, 1))
    
    # Act
    result = create_trajectory_point_cloud(trajectory)

    # Assert
    assert TrajectoryPointCloud == type(trajectory)
    assert 20 == len(result)