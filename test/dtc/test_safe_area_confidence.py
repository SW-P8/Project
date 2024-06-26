from DTC.construct_safe_area import SafeArea
from datetime import datetime, timedelta
from DTC.point import Point

import pytest

class TestSafeArea():
    @pytest.fixture
    def default_safe_area(self):
        cover_set = {(5, 5)}
        safe_area = SafeArea.from_cover_set(cover_set, (5, 5), decrease_factor=0.1, timestamp=datetime.now(), confidence_change=0.01, cardinality_squish=0.1, max_confidence_change=0.1)
        return safe_area

    def test_calculate_confidence_decrease(self, default_safe_area):
        default_safe_area.radius = 5

        res = round(default_safe_area.calculate_confidence_decrease(0.1), 5)
        assert res == 0.02000

    def test_calculate_confidence_decrease_determined_by_min_confidence(self, default_safe_area):
        default_safe_area.radius = 0.02

        res = round(default_safe_area.calculate_confidence_decrease(0.8), 5)
        assert res == 0.025

    def test_set_confidence(self, default_safe_area):
        new_time = datetime.now() + timedelta(minutes=2)
        default_safe_area.set_confidence(0.2, new_time)

        assert default_safe_area.confidence == 0.2
        assert default_safe_area.timestamp == new_time

    # Test that confidence should be impacted over time.
    def test_get_confidence_and_time_change_over_time(self, default_safe_area):
        new_time = datetime.now() + timedelta(hours=0)
        
        # Should not change, as time is unchanged.
        assert (1, new_time) == default_safe_area.get_current_confidence(new_time)

        new_time = datetime.now() + timedelta(hours=100)
        
        assert (1, new_time) != default_safe_area.get_current_confidence(new_time)

    def test_update_confidence_outside_radius(self, default_safe_area):
        test_point = Point(10, 10, datetime.now())
        default_safe_area.cardinality = 10

        start_cardinality = default_safe_area.cardinality
        start_confidence = default_safe_area.confidence
        
        default_safe_area.update_confidence(10, test_point)

        # Cardinality should not change as it is not within radius of safe area.
        assert start_cardinality == default_safe_area.cardinality 
        assert start_confidence > default_safe_area.confidence

    def test_update_confidence_inside_radius(self, default_safe_area):
        test_point = Point(5.5, 5.5, datetime.now())
        default_safe_area.confidence = 0.5
        default_safe_area.cardinality = 10

        start_cardinality = default_safe_area.cardinality
        start_confidence = default_safe_area.confidence

        default_safe_area.update_confidence(0.5, test_point)
        
        # Cardinality should change as it is within radius of safe area.
        assert start_cardinality < default_safe_area.cardinality
        assert start_cardinality + 1 == default_safe_area.cardinality
        assert start_confidence < default_safe_area.confidence

    def test_calculate_time_decay_do_not_change(self, default_safe_area):
        default_safe_area.cardinality = 10
        
        assert 0 == default_safe_area.calculate_time_decay(0.1)


    def test_calculate_time_decay_change(self, default_safe_area):
        default_safe_area.cardinality = 10
        default_safe_area.decay_factor = 0.1

        assert 0 < default_safe_area.calculate_time_decay(1)

    def test_calculate_time_decay_change_with_delta(self, default_safe_area):
        default_safe_area.cardinality = 10
        default_safe_area.decay_factor = 0.1
        
        decay_low = default_safe_area.calculate_time_decay(0.1)
        decay_high = default_safe_area.calculate_time_decay(1)
        
        assert decay_low < decay_high