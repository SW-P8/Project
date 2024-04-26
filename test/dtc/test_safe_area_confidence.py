from DTC.construct_safe_area import SafeArea
from datetime import datetime, timedelta
from DTC.point import Point

import pytest

class TestSafeArea():
    @pytest.fixture
    def default_safe_area(self):
        cover_set = {(5, 5)}
        return SafeArea(cover_set, (5, 5), decrease_factor=0.1, confidence_change=0.01, normalisation_factor=100000, cardinality_squish=0.1, max_confidence_change=0.1)

    @pytest.mark.parametrize("normalised_cardinality, expected_result",
        [
            (0.001, -0.053),# test with values for cardinality_offset with cardinality = 100
            (1, 0.019),     # test with values for cardinality_offset with cardinality = 100.000
            (3, 0.400),     # test with values for cardinality_offset with cardinality = 300.000
            (10, 0.899)     # test with values for cardinality_offset with cardinality = 1.000.000
        ]
    )
    def test_sigmoid_as_used_for_cardinality_offset(self, normalised_cardinality, expected_result, default_safe_area):
        # Arrange
        x_offset = 3
        y_offset = -0.1
        multiplier = 1

        # Act
        result = default_safe_area.sigmoid(normalised_cardinality, x_offset, y_offset, multiplier)

        # Assert
        assert round(result, 3) == expected_result

    # Test for decay with delta = 0.05 and x_offset from test_sigmoid_as_used_for_cardinality_offset.
    @pytest.mark.parametrize("x_offset, expected_result",
        [
            (-0.053, 0.556),    # test with values for cardinality_offset with cardinality = 100
            (0.019, 0.530),     # test with values for cardinality_offset with cardinality = 100.000
            (0.400, 0.38),      # test with values for cardinality_offset with cardinality = 300.000
            (0.899, 0.149)      # test with values for cardinality_offset with cardinality = 1.000.000
        ]
    )
    def test_sigmoid_as_used_for_decay_with_delta_0_05(self, x_offset, expected_result, default_safe_area):
        # Arrange
        delta_decay = (1 / 60 * 60 * 24) * 0.05
        y_offset = -0.5
        multiplier = 2

        #Act
        result = default_safe_area.sigmoid(delta_decay, x_offset, y_offset, multiplier)

        # Assert
        assert round(result, 3) == expected_result

    def test_confidense_increase_determined_by_max_confidence_change(self, default_safe_area):
        default_safe_area.cardinality = 10
        assert default_safe_area.get_confidence_increase() == 0.1

    def test_confidense_increase_changed_less_than_max(self, default_safe_area):
        default_safe_area.cardinality = 100000
        assert default_safe_area.get_confidence_increase() == 0.01

    def test_calculate_confidence_decrease(self, default_safe_area):
        default_safe_area.radius = 5

        res = round(default_safe_area.calculate_confidence_decrease(0.1), 5)
        assert res == 0.00300

    def test_calculate_confidence_decrease_determined_by_min_confidence(self, default_safe_area):
        default_safe_area.radius = 0.02

        res = round(default_safe_area.calculate_confidence_decrease(0.8), 5)
        assert res == 0.15

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