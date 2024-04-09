import pytest
import database.db as db
import datetime
from database.taxi_data_handler import TaxiDataHandler

class TestDataHandler():
    @pytest.fixture
    def dal(self) -> TaxiDataHandler:
        connection = db.init_db()
        db.seed_db(connection)
        return TaxiDataHandler(connection)

    def test_dev_seed(self, dal: TaxiDataHandler):
        res = dal.read_records_by_taxi_id(1)
        assert len(res) == 9
    
    def test_read_by_trajectory_id(self, dal:TaxiDataHandler):
        res1 = dal.read_records_by_trajectory_id(1)
        res2 = dal.read_records_by_trajectory_id(2)

        assert len(res1) == 7
        assert len(res2) == 2

    def test_read_n_records(self, dal:TaxiDataHandler):
        res1 = dal.read_n_records(4)
        res2 = dal.read_n_records(9)

        assert len(res1) == 4
        assert len(res2) == 9
    
    def test_read_n_records_inside_bbb(self, dal: TaxiDataHandler):
        res1 = dal.read_n_records_inside_bbb(12)
        res2 = dal.read_n_records_inside_bbb(15)

        assert len(res1) == 10
        assert len(res2) == 10

               

    def test_adding_record(self, dal: TaxiDataHandler):
        dal.create_record(420, datetime.datetime(2024, 3, 19, 14, 3, 0), 69, 67, 1337)
        res = dal.read_records_by_taxi_id(420)
        assert res == [(420, datetime.datetime(2024, 3, 19, 14, 3), 69.0, 67.0, 1337)]
    
    def test_delete_taxi(self, dal: TaxiDataHandler):
        res_before_delete = dal.read_records_by_taxi_id(1)
        dal.delete_taxi_records(1)
        res_after_delete = dal.read_records_by_taxi_id(1)

        assert len(res_before_delete) == 9
        assert len(res_after_delete) == 0
    
    def test_delete_trajectory(self, dal: TaxiDataHandler):
        res_before_delete = dal.read_records_by_trajectory_id(1)
        dal.delete_trajectory_records(1)
        res_after_delete = dal.read_records_by_trajectory_id(1)

        assert len(res_before_delete) == 7
        assert len(res_after_delete) == 0

