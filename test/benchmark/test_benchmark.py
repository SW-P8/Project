import pytest

from DTC import dtc_executor
from database import db
from database import load_data
from database.taxi_data_handler import TaxiDataHandler

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "bm_cheap: Run tests with 1,000,000 points"
    )
    config.addinivalue_line(
        "markers", "bm_mid: Run tests with 10,000,000 points"
    )
    config.addinivalue_line(
        "markers", "bm_expensive: Run tests with all points"
    )

@pytest.fixture(scope="session")
def connection_pool():
    conn = db.init_db()
    try:
        yield conn
    finally:
        conn.closeall

@pytest.fixture(scope="session")
def start_up(request, connection_pool):
    limit = 0
    for item in request.session.items:
        print(item.get_closest_marker)
        if item.get_closest_marker('bm_expensive') is not None:
            limit = 0
        elif item.get_closest_marker('bm_mid') is not None:
            limit = 3000
        elif item.get_closest_marker('bm_cheap') is not None:
            limit = 1000

    
    load_data.load_data_from_csv(connection_pool, limit)
    taxiDataHandler = TaxiDataHandler(connection_pool)
    yield taxiDataHandler
    

@pytest.fixture(scope="function")
def small_points(start_up, request):
    def _small_points():
        return start_up.read_n_records(1000000)
    yield _small_points

@pytest.fixture(scope="function")
def medium_points(start_up, request):
    def _medium_points():
        print("Executing medium lazy fixture")
        return start_up.read_n_records(5000000)
    yield _medium_points

@pytest.fixture(scope="function")
def large_points(start_up, request):
    def _large_points():
        print("Executing large lazy fixture")
        return start_up.read_n_records(0)
    yield _large_points

@pytest.mark.bm_mid
def test_read_from_database_mid(medium_points, benchmark):
    data = benchmark.pedantic(medium_points, rounds=4, iterations=1, warmup_rounds=0)
    assert data != None

@pytest.mark.bm_expensive
def test_read_from_database_large(large_points, benchmark):
    data = benchmark.pedantic(large_points, rounds=4, iterations=1, warmup_rounds=0)
    assert data != None

@pytest.mark.bm_cheap
def test_dtc(small_points, benchmark):
    data = benchmark.pedantic(small_points, rounds=4, iterations=1, warmup_rounds=0)
    pc = dtc_executor.TrajectoryPointCloud()
