import pytest

def pytest_addoption(parser):
    parser.addoption(
        "--benchmark-cheap", action="store_true", default=False, help="run cheap benchmarks"
    )
    parser.addoption(
        "--benchmark-mid", action="store_true", default=False, help="run mid benchmarks"
    )
    parser.addoption(
        "--benchmark", action="store_true", default=False, help="run full benchmarks"
    )

def pytest_configure(config):
    config.addinivalue_line("markers", "bm_cheap: mark a test as cheap benchmark.")
    config.addinivalue_line("markers", "bm_mid: mark a test as medium benchmark.")
    config.addinivalue_line("markers", "bm_expensive: mark a test as expensive benchmark.")

def pytest_collection_modifyitems(config, items):
    skip_bm_cheap = pytest.mark.skip(reason="Benchmarking limited to --benchmark-cheap.")
    skip_bm_mid = pytest.mark.skip(reason="Benchmarking limited to --benchmark-mid")
    skip_bm_expensive = pytest.mark.skip(reason="Benchmarking limited to --benchmark")

    if config.getoption("--benchmark-cheap"):
        for item in items:
            if "bm_mid" in item.keywords:
                item.add_marker(skip_bm_mid)
            if "bm_expensive" in item.keywords:
                item.add_marker(skip_bm_expensive)
        return
    elif config.getoption("--benchmark-mid"):
        for item in items:
            if "bm_cheap" in item.keywords:
                item.add_marker(skip_bm_cheap)
            if "bm_expensive" in item.keywords:
                item.add_marker(skip_bm_expensive)

        return
    elif config.getoption("--benchmark"):
        for item in items:
            if "bm_cheap" in item.keywords:
                item.add_marker(skip_bm_cheap)
            if "bm_mid" in item.keywords:
                item.add_marker(skip_bm_mid)
        return

    for item in items:
        if "bm_cheap" in item.keywords:
            item.add_marker(skip_bm_cheap)
        if "bm_mid" in item.keywords:
            item.add_marker(skip_bm_mid)
        if "bm_expensive" in item.keywords:
            item.add_marker(skip_bm_expensive)