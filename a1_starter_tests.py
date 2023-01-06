import pytest
from typing import Dict
from distance_map import DistanceMap
from domain import Truck, Parcel, Fleet
from scheduler import GreedyScheduler
from container import PriorityQueue, _shorter
from experiment import SchedulingExperiment

# This variable is used in the special pytest test case defined by function
# test_experiment below.  The variable defines a single scheduling experiment
# test case to be run. It gives a unique identifier for the test case, and
# specifies both the configuration to use and the correct statistics to expect.
test_arguments = [
    ('1-small',
     {
         'depot_location': 'Toronto',
         'parcel_file': 'data/parcel-data-small.txt',
         'truck_file': 'data/truck-data-small.txt',
         'map_file': 'data/map-data.txt',
         'algorithm': 'greedy',
         'parcel_priority': 'volume',
         'parcel_order': 'non-decreasing',
         'truck_order': 'non-decreasing',
         'verbose': 'false'
     },
     {
         'fleet': 3,
         'unused_trucks': 0,
         'unused_space': 0,
         'avg_distance': 192.7,
         'avg_fullness': 100,
         'unscheduled': 0
     }),
    # You can add additional test cases here!
    # Write these in the format:
    # (<test_id>, <config dictionary>, <expected_stats dictionary>)
    # If you're adding multiple tests: remember to add a comma (,) after the
    # tuple!
]


def test_distance_map_basic() -> None:
    """Test DistanceMap when a single distance is provided."""
    m = DistanceMap()
    assert m.distance('Montreal', 'Toronto') == -1
    m.add_distance('Montreal', 'Toronto', 4)
    assert m.distance('Montreal', 'Toronto') == 4


def test_num_trucks_doctest() -> None:
    """Test the doctest provided for Fleet.num_trucks"""
    f = Fleet()
    t1 = Truck(1423, 10, 'Toronto')
    f.add_truck(t1)
    assert f.num_trucks() == 1

def test_num_trucks_0() -> None:
    """Test num_trucks with 0 trucks"""
    f = Fleet()
    asset f.num_trucks == 0
  

def test_num_trucks_change() -> None:
    """Test num_trucks after somethings been added"""
    f = Fleet()
    t1 = Truck(1234, 20, 'Toronto')
    t2 = Truck(1254, 22, 'Los Angeles')
    f.add_truck(t1)
    f.add_truck(t2)
    assert f.num_trucks() == 2
    
    t3 = Truck(1254, 22, 'Toronto')
    f.add_truck(t3)
    assert f.num_trucks() == 3
    
    
def test_num_nonempty_trucks_doctest() -> None:
    """Test the doctest provided for Fleet.num_nonempty_trucks"""
    f = Fleet()

    t1 = Truck(1423, 10, 'Toronto')
    f.add_truck(t1)
    p1 = Parcel(1, 5, 'Buffalo', 'Hamilton')
    assert t1.pack(p1) is True

    p2 = Parcel(2, 4, 'Toronto', 'Montreal')
    assert t1.pack(p2) is True
    assert t1.fullness() == 90.0

    t2 = Truck(5912, 20, 'Toronto')
    f.add_truck(t2)
    p3 = Parcel(3, 2, 'New York', 'Windsor')
    assert t2.pack(p3) is True
    assert t2.fullness() == 10.0

    t3 = Truck(1111, 50, 'Toronto')
    f.add_truck(t3)
    assert f.num_nonempty_trucks() == 2
    
def test_num_nonempty_trucks_all_full() -> None:
    """Tests num_nonempty_trucks when one truck is empty and one is nonempty"""
    f = Fleet()

    t1 = Truck(1423, 10, 'Toronto')
    f.add_truck(t1)
    p1 = Parcel(1, 5, 'Buffalo', 'Hamilton')
    assert t1.pack(p1) is True

    t3 = Truck(1111, 50, 'Toronto')
    f.add_truck(t3)
    assert f.num_nonempty_trucks() == 1
    
    
def test_num_nonempty_trucks_all_empty() -> None:
    """Tests num_nonempty_trucks when all trucks are empty"""
    t1 = Truck(1111, 50, 'Toronto')
    f.add_truck(t1)

    t3 = Truck(1234, 50, 'Toronto')
    f.add_truck(t3)

    t3 = Truck(2342, 50, 'Toronto')
    f.add_truck(t3)
    assert f.num_nonempty_trucks() == 0

    
def test_parcel_allocations_doctest() -> None:
    """Test the doctest provided for Fleet.parcel_allocations"""
    f = Fleet()
    t1 = Truck(1423, 10, 'Toronto')
    p1 = Parcel(27, 5, 'Toronto', 'Hamilton')
    p2 = Parcel(12, 5, 'Toronto', 'Hamilton')
    assert t1.pack(p1) is True
    assert t1.pack(p2) is True
    t2 = Truck(1333, 10, 'Toronto')
    p3 = Parcel(28, 5, 'Toronto', 'Hamilton')
    assert t2.pack(p3) is True
    f.add_truck(t1)
    f.add_truck(t2)
    assert f.parcel_allocations() == {1423: [27, 12], 1333: [28]}


def test_total_unused_space_doctest() -> None:
    """Test the doctest provided for Fleet.total_unused_space"""
    f = Fleet()
    assert f.total_unused_space() == 0

    t = Truck(1423, 1000, 'Toronto')
    p = Parcel(1, 5, 'Buffalo', 'Hamilton')
    assert t.pack(p) is True

    f.add_truck(t)
    assert f.total_unused_space() == 995
    
    
def test_total_unused_space_full() -> None:
    """Test total_unused_space when all trucks are full"""
    f = Fleet()
    t1 = Truck(1423, 5, 'Toronto')
    p1 = Parcel(1, 5, 'Buffalo', 'Hamilton')
    t1.pack(p1) 
    f.add_truck(t1)
    
    t2 = Truck(1000, 5, 'Toronto')
    p2 = Parcel(4, 5, 'Buffalo', 'Hamilton')
    t2.pack(p2) 
    f.add_truck(t2)
    
    t3 = Truck(4321, 4, 'Toronto')
    p3 = Parcel(1, 4, 'Buffalo', 'Hamilton')
    t3.pack(p3) 
    f.add_truck(t3)
    
    assert f.total_unused_space() == 0
    
    
def test_total_unused_space_empty() -> None:
    """Test total_unused_space when all trucks are empty"""
    f = Fleet()
    t1 = Truck(1423, 5, 'Toronto')
    f.add_truck(t1)
    
    t2 = Truck(1000, 5, 'Toronto')
    f.add_truck(t2)
    
    t3 = Truck(4321, 4, 'Toronto')
    f.add_truck(t3)
    
    assert f.total_unused_space() == 14
    
  
def test_total_unused_space_no_space() -> None:
    """Test total_unused_space when all trucks don't have capacity"""
    f = Fleet()
    t1 = Truck(1423, 0, 'Toronto')
    f.add_truck(t1)
    
    t2 = Truck(1000, 0, 'Toronto')
    f.add_truck(t2)
    
    t3 = Truck(4321, 0, 'Toronto')
    f.add_truck(t3)
    
    assert f.total_unused_space() == 0
    
    
def test_average_fullness_doctest() -> None:
    """Test the doctest provided for Fleet.average_fullness"""
    f = Fleet()
    t = Truck(1423, 10, 'Toronto')
    p = Parcel(1, 5, 'Buffalo', 'Hamilton')
    assert t.pack(p) is True

    f.add_truck(t)
    assert f.average_fullness() == 50.0
   

def test_average_fullness_doctest() -> None:
    """Test average_fullness when fleet is empty"""
    f = Fleet()
    assert f.average_fullness() == 0.0

 """   
def test_divide_by_zero_fullness() -> None:
    #Test for a divide by 0 error
    t = Truck(1423, 0, 'Toronto')
    p = Parcel(1, 5, 'Buffalo', 'Hamilton')
    assert t.pack(p) is True
    assert t.fullness() is ZeroDivisionError
"""

def test_total_distance_travelled_doctest() -> None:
    """Test the doctest provided for Fleet.total_distance_travelled"""
    f = Fleet()
    t1 = Truck(1423, 10, 'Toronto')
    p1 = Parcel(1, 5, 'Toronto', 'Hamilton')
    assert t1.pack(p1) is True

    t2 = Truck(1333, 10, 'Toronto')
    p2 = Parcel(2, 5, 'Toronto', 'Hamilton')
    assert t2.pack(p2) is True

    m = DistanceMap()
    m.add_distance('Toronto', 'Hamilton', 9)
    f.add_truck(t1)
    f.add_truck(t2)
    assert f.total_distance_travelled(m) == 36

    
def test_total_distance_travelled_negative() -> None:
    """Test total_distance_travelled when a distance is negative"""
    f = Fleet()
    t1 = Truck(1423, 10, 'Toronto')
    p1 = Parcel(1, 5, 'Toronto', 'Hamilton')
    assert t1.pack(p1) is True

    t2 = Truck(1333, 10, 'Toronto')
    p2 = Parcel(2, 5, 'Toronto', 'Hamilton')
    assert t2.pack(p2) is True

    m = DistanceMap()
    m.add_distance('Toronto', 'Hamilton', -9)
    f.add_truck(t1)
    f.add_truck(t2)
    assert f.total_distance_travelled(m) == 36
    
    
def test_total_distace_travelled_0() -> None:
    """Test total_distance_travelled when one distance is 0"""
    f = Fleet()
    t1 = Truck(1423, 10, 'Toronto')
    p1 = Parcel(1, 5, 'Toronto', 'Hamilton')
    assert t1.pack(p1) is True

    t2 = Truck(1333, 10, 'Toronto')
    p2 = Parcel(2, 5, 'Toronto', 'Toronto')
    assert t2.pack(p2) is True

    m = DistanceMap()
    m.add_distance('Toronto', 'Hamilton', 9)
    m.add_distance('Toronto', 'Toronto', 0)
    f.add_truck(t1)
    f.add_truck(t2)
    assert f.total_distance_travelled(m) == 18
    
    
def test_total_distace_travelled_none() -> None:
    """Test total_distance_travelled when distance is 0"""
    f = Fleet()
    t = Truck(1333, 10, 'Toronto')
    p = Parcel(2, 5, 'Toronto', 'Toronto')
    assert t.pack(p) is True

    m = DistanceMap()
    m.add_distance('Toronto', 'Toronto', 0)
    f.add_truck(t)
    assert f.total_distance_travelled(m) == 00
    
    
def test_average_distance_travelled_doctest() -> None:
    """Test the doctest provided for Fleet.average_distance_travelled"""
    f = Fleet()
    t1 = Truck(1423, 10, 'Toronto')
    p1 = Parcel(1, 5, 'Toronto', 'Hamilton')
    assert t1.pack(p1) is True

    t2 = Truck(1333, 10, 'Toronto')
    p2 = Parcel(2, 5, 'Toronto', 'Hamilton')
    assert t2.pack(p2) is True

    m = DistanceMap()
    m.add_distance('Toronto', 'Hamilton', 9)
    f.add_truck(t1)
    f.add_truck(t2)
    assert f.average_distance_travelled(m) == 18.0
    
    
 """   
def test_average_distance_travelled_ZeroDivisionError() -> None:
    #Test average_distance_travelled for /0
    f = Fleet()

    t2 = Truck(1333, 10, 'Toronto')
    p2 = Parcel(2, 5, 'Toronto', 'Toronto')
    assert t2.pack(p2) is True

    m = DistanceMap()
    m.add_distance('Toronto', 'Hamilton', 10)
    
    if f.trucks == []:
        assert f.average_distance_travelled(m) is ZeroDivisionError
"""


def test_priority_queue_is_empty_doctest() -> None:
    """Test the doctest provided for PriorityQueue.is_empty"""
    pq = PriorityQueue(str.__lt__)
    assert pq.is_empty() is True

    pq.add('fred')
    assert pq.is_empty() is False


def test_priority_queue_add_remove_doctest() -> None:
    """Test the doctest provided for PriorityQueue.add and
    PriorityQueue.remove"""
    pq = PriorityQueue(_shorter)
    pq.add('fred')
    pq.add('arju')
    pq.add('monalisa')
    pq.add('hat')
    assert pq.remove() == 'hat'
    assert pq.remove() == 'fred'
    assert pq.remove() == 'arju'
    assert pq.remove() == 'monalisa'
    
    
def test_priority_queue() -> None:
    """Tests if it prioritizes things correctly"""
    pq = PriorityQueue(_shorter)
    pq.add('abc')
    pq.add('efgh')
    pq.add('ijk')
    pq.add('l')
    assert pq.remove() == 'l'
    assert pq.remove() == 'abc'
    assert pq.remove() == 'ijk'
    assert pq.remove() == 'efgh'
    
        
def test_priority_queue_all_same_size() -> None:
    """Tests if pq is FIFO"""
    pq = PriorityQueue(_shorter)
    pq.add('abc')
    pq.add('def')
    pq.add('ghi')
    assert pq.remove() == 'abc'
    assert pq.remove() == 'def'
    assert pq.remove() == 'ghi'
    
    
def test_priority_queue_different_sizes() -> None:
    """Tests if pq sorts by length"""
    pq = PriorityQueue(_shorter)
    pq.add('abc')
    pq.add('de')
    pq.add('f')
    assert pq.remove() == 'f'
    assert pq.remove() == 'de'
    assert pq.remove() == 'abc'
    
    
def test_greedy_scheduler_example() -> None:
    """Test GreedyScheduler on the example provided."""
    p17 = Parcel(17, 25, 'York', 'Toronto')
    p21 = Parcel(21, 10, 'York', 'London')
    p13 = Parcel(13, 8, 'York', 'London')
    p42 = Parcel(42, 20, 'York', 'Toronto')
    p25 = Parcel(25, 15, 'York', 'Toronto')
    p61 = Parcel(61, 15, 'York', 'Hamilton')
    p76 = Parcel(76, 20, 'York', 'London')

    t1 = Truck(1, 40, 'York')
    t2 = Truck(2, 40, 'York')
    t3 = Truck(3, 25, 'York')

    f = Fleet()
    f.add_truck(t1)
    f.add_truck(t2)
    f.add_truck(t3)

    # We've left parcel_file, truck_file, and map_file empty in the config
    # dictionary below because you should *not* use these in your
    # GreedyScheduler. It is not responsible for reading data from these files.
    config = {'depot_location': 'York',
              'parcel_file': '',
              'truck_file': '',
              'map_file': '',
              'algorithm': 'greedy',
              'parcel_priority': 'destination',
              'parcel_order': 'non-increasing',
              'truck_order': 'non-increasing',
              'verbose': 'false'}

    scheduler = GreedyScheduler(config)
    unscheduled = scheduler.schedule([p17, p21, p13, p42, p25, p61, p76],
                                     [t1, t2, t3])

    assert unscheduled == [p76]

    truck_parcels = f.parcel_allocations()
    assert truck_parcels[1] == [17, 61]
    assert truck_parcels[2] == [42, 25]
    assert truck_parcels[3] == [21, 13]

    
    def test_greedy_scheduler_no_space() -> None:
    """Test GreedyScheduler on the example provided."""
    p17 = Parcel(17, 25, 'York', 'Toronto')
    p21 = Parcel(21, 10, 'York', 'London')
    p13 = Parcel(13, 8, 'York', 'London')
    p42 = Parcel(42, 20, 'York', 'Toronto')
    p25 = Parcel(25, 15, 'York', 'Toronto')
    p61 = Parcel(61, 15, 'York', 'Hamilton')
    p76 = Parcel(76, 20, 'York', 'London')

    t1 = Truck(1, 1, 'York')
    t2 = Truck(2, 2, 'York')
    t3 = Truck(3, 3, 'York')

    f = Fleet()
    f.add_truck(t1)
    f.add_truck(t2)
    f.add_truck(t3)

    config = {'depot_location': 'York',
              'parcel_file': '',
              'truck_file': '',
              'map_file': '',
              'algorithm': 'greedy',
              'parcel_priority': 'destination',
              'parcel_order': 'non-increasing',
              'truck_order': 'non-increasing',
              'verbose': 'false'}

    scheduler = GreedyScheduler(config)
    unscheduled = scheduler.schedule([p17, p21, p13, p42, p25, p61, p76],
                                     [t1, t2, t3])

    assert unscheduled == [p17, p21, p13, p42, p25, p61, p76]

    #incomplete
    def test_greedy_scheduler_dest_noninc_nondec() -> None:
    """Test GreedyScheduler parcel order set to non-increasing and truck order set to non-decreasing."""
    p17 = Parcel(17, 25, 'York', 'Toronto')
    p21 = Parcel(21, 10, 'York', 'London')
    p13 = Parcel(13, 8, 'York', 'London')
    p42 = Parcel(42, 20, 'York', 'Toronto')
    p25 = Parcel(25, 15, 'York', 'Toronto')
    p61 = Parcel(61, 15, 'York', 'Hamilton')
    p76 = Parcel(76, 20, 'York', 'London')

    t1 = Truck(1, 40, 'York')
    t2 = Truck(2, 40, 'York')
    t3 = Truck(3, 25, 'York')

    f = Fleet()
    f.add_truck(t1)
    f.add_truck(t2)
    f.add_truck(t3)

    # We've left parcel_file, truck_file, and map_file empty in the config
    # dictionary below because you should *not* use these in your
    # GreedyScheduler. It is not responsible for reading data from these files.
    config = {'depot_location': 'York',
              'parcel_file': '',
              'truck_file': '',
              'map_file': '',
              'algorithm': 'greedy',
              'parcel_priority': 'destination',
              'parcel_order': 'non-increasing',
              'truck_order': 'non-decreasing',
              'verbose': 'false'}

    scheduler = GreedyScheduler(config)
    unscheduled = scheduler.schedule([p17, p21, p13, p42, p25, p61, p76],
                                     [t1, t2, t3])

    assert unscheduled == [p76]

    truck_parcels = f.parcel_allocations()
    assert truck_parcels[1] == [17, 61]
    assert truck_parcels[2] == [42, 25]
    assert truck_parcels[3] == [21, 13]
    
    
    #incomplete
    def test_greedy_scheduler_dest_nondec_nondec() -> None:
    """Test GreedyScheduler parcel order set to non-increasing and truck order set to non-decreasing."""
    p17 = Parcel(17, 25, 'York', 'Toronto')
    p21 = Parcel(21, 10, 'York', 'London')
    p13 = Parcel(13, 8, 'York', 'London')
    p42 = Parcel(42, 20, 'York', 'Toronto')
    p25 = Parcel(25, 15, 'York', 'Toronto')
    p61 = Parcel(61, 15, 'York', 'Hamilton')
    p76 = Parcel(76, 20, 'York', 'London')

    t1 = Truck(1, 40, 'York')
    t2 = Truck(2, 40, 'York')
    t3 = Truck(3, 25, 'York')

    f = Fleet()
    f.add_truck(t1)
    f.add_truck(t2)
    f.add_truck(t3)

    # We've left parcel_file, truck_file, and map_file empty in the config
    # dictionary below because you should *not* use these in your
    # GreedyScheduler. It is not responsible for reading data from these files.
    config = {'depot_location': 'York',
              'parcel_file': '',
              'truck_file': '',
              'map_file': '',
              'algorithm': 'greedy',
              'parcel_priority': 'destination',
              'parcel_order': 'non-decreasing',
              'truck_order': 'non-decreasing',
              'verbose': 'false'}

    scheduler = GreedyScheduler(config)
    unscheduled = scheduler.schedule([p17, p21, p13, p42, p25, p61, p76],
                                     [t1, t2, t3])

    assert unscheduled == [p76]

    truck_parcels = f.parcel_allocations()
    assert truck_parcels[1] == [17, 61]
    assert truck_parcels[2] == [42, 25]
    assert truck_parcels[3] == [21, 13]
    
    
    #incomplete
    def test_greedy_scheduler_dest_nondec_noninc() -> None:
    """Test GreedyScheduler parcel order set to non-increasing and truck order set to non-decreasing."""
    p17 = Parcel(17, 25, 'York', 'Toronto')
    p21 = Parcel(21, 10, 'York', 'London')
    p13 = Parcel(13, 8, 'York', 'London')
    p42 = Parcel(42, 20, 'York', 'Toronto')
    p25 = Parcel(25, 15, 'York', 'Toronto')
    p61 = Parcel(61, 15, 'York', 'Hamilton')
    p76 = Parcel(76, 20, 'York', 'London')

    t1 = Truck(1, 40, 'York')
    t2 = Truck(2, 40, 'York')
    t3 = Truck(3, 25, 'York')

    f = Fleet()
    f.add_truck(t1)
    f.add_truck(t2)
    f.add_truck(t3)

    # We've left parcel_file, truck_file, and map_file empty in the config
    # dictionary below because you should *not* use these in your
    # GreedyScheduler. It is not responsible for reading data from these files.
    config = {'depot_location': 'York',
              'parcel_file': '',
              'truck_file': '',
              'map_file': '',
              'algorithm': 'greedy',
              'parcel_priority': 'destination',
              'parcel_order': 'non-decreasing',
              'truck_order': 'non-increasing',
              'verbose': 'false'}

    scheduler = GreedyScheduler(config)
    unscheduled = scheduler.schedule([p17, p21, p13, p42, p25, p61, p76],
                                     [t1, t2, t3])

    assert unscheduled == [p76]

    truck_parcels = f.parcel_allocations()
    assert truck_parcels[1] == [17, 61]
    assert truck_parcels[2] == [42, 25]
    assert truck_parcels[3] == [21, 13]
################################################################################
# The test below uses pytest.mark.parametrize.
#
# This provides a way of running the same test code with different parameters
# without having to repeat the body multiple times.
#
# The line above the test_experiment method works as follows:
# @pytest.mark.parametrize('test_id, config, expected_stats', test_arguments)
#                           ^                                 ^
#                    These are the parameters        This is a list where each
#                    of test_experiment that         element is a tuple
#                    we're filling.                  containing values for those
#                                                    parameters.
#
# test_arguments is the variable defined near the top of this module.
#
# We have included one item in test_arguments for you. This is a tuple
# representing the following parameter configurations:
#     test_id        = '1-small'
#     config         = {'depot_location': 'Toronto', ...}
#     expected_stats = {'fleet': 3, ...}
#
# If you want to add additional test cases, you create a tuple with the same
# format and add it to the list.
#
# For more details, see:
# https://docs.pytest.org/en/stable/parametrize.html
#
# NOTE: if you get a "FileNotFoundError", try replacing the filename
# with the full path to the file (e.g., "C:\\Users\\David\\Documents\\...")
################################################################################
@pytest.mark.parametrize('stat', [
    'fleet', 'unused_trucks', 'unused_space', 'avg_distance', 'avg_fullness',
    'unscheduled'])
class TestExperiment:
    """
    Tests for SchedulingExperiment.run
    """
    @pytest.mark.parametrize('test_id, config, expected_stats', test_arguments)
    def test_experiment(self, test_id: str, config: Dict[str, str],
                        expected_stats: Dict[str, str], stat: str) -> None:
        """Run the SchedulingExperiment on the given config and expected_stats.
        Assert that the stat returned from the experiment matches
        expected_stats[stat].
        """
        experiment = SchedulingExperiment(config)
        results = experiment.run()

        # pytest.approx lets us use approximate values so we can avoid
        # failing a test case over very small differences in floating point
        # values. These can arise simply from doing mathematical operations in
        # a different order. [If you find this intriguing, take csc336!]

        # In this case, we're making sure our actual value is in the range
        # (expected - 1e-1, expected + 1e-1)
        expected = expected_stats[stat]
        actual = results[stat]
        assert actual == pytest.approx(expected, abs=1e-1)


if __name__ == '__main__':
    pytest.main(['a1_starter_tests.py'])
