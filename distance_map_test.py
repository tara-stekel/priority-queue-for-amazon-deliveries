import pytest
from typing import Dict
from distance_map import DistanceMap


def test_neg_distance() -> None:
    """"Test it boi"""
    m = DistanceMap()
    m.add_distance('Toronto', 'Hamilton', -9)
    assert m.distance('Toronto', 'Hamilton') == 9

def test_add_distance_normal() -> None:
    """Testing if this shit even works normally"""
    m = DisntaceMap()
    m.add_distance('Toronto', 'Hamilton', 9)
    assert m.distance('Toronto', 'Hamilton') == 9
    
def test_one_city() -> None:
    """"Test it boi"""
    m = DistanceMap()
    m.add_distance('Toronto', None, 9)
    assert m.distance('Toronto', 'Hamilton') == 0


def test_none() -> None:
    """"Test it boi"""
    m = DistanceMap()
    m.add_distance('Toronto', 'Hamilton', None)
    assert m.distance('Toronto', 'Hamilton') == 0


def test_city_not_str() -> None:
    """"Test it boi"""


if __name__ == '__main__':
    pytest.main(['distance_map_test.py'])
