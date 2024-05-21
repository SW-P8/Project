import pytest
from DTC.noise_correction import NoiseCorrection

class TestThroughputBenchmark:
    @pytest.mark.bm_throughput
    def test_cleaning_throughput(self, benchmark):
        trajectory = None
        noise_corrector = NoiseCorrection()
        benchmark.pedantic(noise_corrector.noise_detection, kwargs={'trajectory':trajectory}, rounds=5, iterations=3, warmup_rounds=0)
        print("cleaning yup")

    @pytest.mark.bm_throughput
    def test_iterating_throughput(self, benchmark):
        trajectory = None
        print("iterating yup")