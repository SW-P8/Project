import pytest

def pytest_addoption(parser):
    parser.addoption("--marker", action="store", help="Run tests with the specified marker")

def pytest_collection_modifyitems(config, items):
    marker = config.getoption("--marker")
    if marker:
        selected_items = []
        for item in items:
            if marker in item.keywords:
                selected_items.append(item)
        items[:] = selected_items

def pytest_configure(config):
    config.addinivalue_line(
        "markers", "bm_cheap: Run tests with 100 points"
    )
    config.addinivalue_line(
        "markers", "bm_mid: Run tests with 10,000 points"
    )
    config.addinivalue_line(
        "markers", "bm_expensive: Run tests with 1,000,000 points"
    )

@pytest.fixture(params=[1, 2, 3], ids=["bm_cheap", "bm_mid", "bm_expensive"])
def mark_param(request):
    return request.param

def test_example(mark_param):
    param = mark_param
    print(f"Running test with parameter {param}")
    assert True  # Placeholder for your actual tests
