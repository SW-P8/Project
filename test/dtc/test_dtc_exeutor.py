import pytest
from database.taxi_data_handler import TaxiDataHandler
from database import db
from DTC.dtc_executor import DTCExecutor

class TestDTCExecutor:
    @pytest.fixture
    def dtc_executor(self) -> DTCExecutor:
        db.init_db()
        return DTCExecutor()
    
    @pytest.mark.parametrize("input_value", range(1, 8))
    def test_create_point_cloud_with_n_points_returns_correctly_with_single_trajectory(self, input_value, dtc_executor: DTCExecutor):
        pc = dtc_executor.create_point_cloud_with_n_points(input_value)
        assert len(pc.trajectories) == 1
        assert len(pc.trajectories[0].points) == input_value

    @pytest.mark.parametrize("input_value, second_trajectory_size", [(8, 1), (9, 2)])
    def test_create_point_cloud_with_n_points_returns_correctly_with_two_trajectories(self, input_value, second_trajectory_size, dtc_executor: DTCExecutor):
        pc = dtc_executor.create_point_cloud_with_n_points(input_value)
        assert len(pc.trajectories) == 2
        assert len(pc.trajectories[0].points) == 7
        assert len(pc.trajectories[1].points) == second_trajectory_size    