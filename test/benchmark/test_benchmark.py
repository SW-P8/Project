import pytest

from DTC.gridsystem import GridSystem
from DTC.trajectory import TrajectoryPointCloud
from DTC.dtc_executor import DTCExecutor
from database import db
from database import load_data
from database.taxi_data_handler import TaxiDataHandler

class BenchmarkData:
    def __init__(self):
        self.point_cloud = None
        self.grid_system = None

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
    
@pytest.fixture(scope="module")
def bm_data():
    data = BenchmarkData()
    return data

@pytest.fixture(scope="function")
def small_points(request):
    return 1000000

@pytest.fixture(scope="function")
def medium_points(request):
    return 5000000

@pytest.fixture(scope="function")
def large_points(request):
    return "ALL"

@pytest.mark.bm_mid
def test_read_from_database_mid(medium_points, benchmark):
    data = benchmark.pedantic(medium_points, rounds=4, iterations=1, warmup_rounds=0)
    assert data != None

@pytest.mark.bm_expensive
def test_read_from_database_large(large_points, benchmark):
    data = benchmark.pedantic(large_points, rounds=4, iterations=1, warmup_rounds=0)
    assert data != None

@pytest.mark.bm_cheap
def test_point_cloud(small_points, benchmark, bm_data):
    runner = DTCExecutor()
    point_cloud = benchmark.pedantic(runner.create_point_cloud_with_n_points, kwargs={'n':small_points},rounds=4, iterations=1, warmup_rounds=0)
    bm_data.point_cloud = point_cloud
    bm_data.grid_system = GridSystem(point_cloud)
    assert point_cloud != None

@pytest.mark.bm_cheap
def test_build_grid_system(benchmark, bm_data):
    benchmark.pedantic(bm_data.grid_system.create_grid_system, rounds=4, iterations=1, warmup_rounds=0)
    assert bm_data.grid_system != None

@pytest.mark.bm_cheap
def test_extract_main_route(benchmark, bm_data):
    benchmark.pedantic(bm_data.grid_system.extract_main_route, rounds=4, iteration=1, warmup_rounds=0)
    assert bm_data.grid_system != None

@pytest.mark.bm_cheap
def test_extract_main_route(benchmark, bm_data):
    benchmark.pedantic(bm_data.grid_system.extract_route_skeleton())
    assert bm_data.grid_system != None

@pytest.mark.bm_cheap
def test_extract_main_route(benchmark, bm_data):
    benchmark.pedantic(bm_data.grid_system.construct_safe_areas())
    assert bm_data.grid_system != None