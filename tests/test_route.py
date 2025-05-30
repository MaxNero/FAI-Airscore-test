from route import in_goal_sector
from obj_factories import TurnpointFactory, TaskFormulaFactory
import math
from pilot.track import GNSSFix
import factory_objects

turnpoints = [
    TurnpointFactory(lat=41.3435, lon=21.2568, radius=400, how='entry', shape='circle', type='launch'),
    TurnpointFactory(lat=41.5778, lon=21.333, radius=22000, how='entry', shape='circle', type='speed'),
    TurnpointFactory(lat=41.5778, lon=21.333, radius=4000),
    TurnpointFactory(lat=41.2448, lon=21.5773, radius=3000),
    TurnpointFactory(lat=41.348, lon=21.3042, radius=3000, how='entry', shape='circle', type='endspeed'),
    TurnpointFactory(lat=41.348, lon=21.3042, radius=100, how='entry', shape='line', type='goal')
]

test_task = factory_objects.test_task()
test_task.turnpoints = turnpoints

short = GNSSFix(
    rawtime=1,
    lat=41.348016666666666, lon=21.304666666666666,
    validity=True, press_alt=1, gnss_alt=1, index=1, extras=None
)
after_and_out = GNSSFix(
    rawtime=1,
    lat=41.34809381046268, lon=21.300493968601263,
    validity=True, press_alt=1, gnss_alt=1, index=1, extras=None
)
inside = GNSSFix(
    rawtime=1,
    lat=41.34809381046268, lon=21.303493968601263,
    validity=True, press_alt=1, gnss_alt=1, index=1, extras=None
)
line = GNSSFix(
    rawtime=1,
    lat=41.348, lon=21.3042,
    validity=True, press_alt=1, gnss_alt=1, index=1, extras=None
)
meter_short_of_tolerance = GNSSFix(
    rawtime=1, 
    lat=41.348, lon=21.30428,
    validity=True, press_alt=1, gnss_alt=1, index=1, extras=None
)
short_but_tolerance = GNSSFix(
    rawtime=1,
    lat=41.348, lon=21.30425,
    validity=True, press_alt=1, gnss_alt=1, index=1, extras=None
)

goal_tp = TurnpointFactory(lat=41.348, lon=21.3042, radius=100)
previous_tp = TurnpointFactory(lat=41.2448, lon=21.5773)


def test_route_distance(task=test_task):
    task.calculate_task_length()
    assert math.isclose(task.distance, 94624.2, abs_tol=1)


def test_opt_route(task=test_task):
    """
    Formula: pwc 2023
    Before SS optimised:
    opt_dist_to_SS = 4798.651565019276
    SS_distance = 73709.90058624979
    opt_dist_to_ESS = 78508.55215126906
    opt_dist_ESS_goal = 2995.34542314732
    opt_dist = 81503.89757441638

    After SS optimised:
    SS_distance = 73131.62642250722
    partial_distances = [0, 4798.651565019276, 23075.062600575504, 58793.64856039375, 78508.55215126906, 81503.89757441638]

    Formula: gap 2025
    Before SS optimised:
    opt_dist_to_SS = 4798.651565019276
    SS_distance = 73708.44282608402
    opt_dist_to_ESS = 78507.0943911033
    opt_dist_ESS_goal = 3000.1797148332676
    opt_dist = 81507.27410593657

    After SS optimised:
    SS_distance = 73708.50704822189
    partial_distances = [0, 4798.651565019276, 23075.062600575504, 58795.43799086131, 78507.0943911033, 81507.27410593657]
    """
    # PWCA
    task.calculate_optimised_task_length()
    assert math.isclose(task.opt_dist, 81503.9, abs_tol=1)
    assert math.isclose(task.opt_dist_to_SS, 4798.7, abs_tol=1)
    assert math.isclose(task.opt_dist_to_ESS, 78508.6, abs_tol=1)

    partial_distances = [0, 4798.7, 23075.1, 58793.6, 78508.6, 81503.9]
    for idx, d in enumerate(task.partial_distance):
        assert math.isclose(d, partial_distances[idx], abs_tol=1)

    # SS Distance Optimization:
    assert math.isclose(task.SS_distance, 73131.6, abs_tol=1)

    # CIVL
    task.formula = TaskFormulaFactory().from_preset('HG', 'GAP2025')
    task.optimised_turnpoints = []
    task.calculate_optimised_task_length()
    assert math.isclose(task.opt_dist, 81507.3, abs_tol=1)
    assert math.isclose(task.opt_dist_to_SS, 4798.7, abs_tol=1)
    assert math.isclose(task.opt_dist_to_ESS, 78507.1, abs_tol=1)

    partial_distances = [0, 4798.7, 23075.1, 58795.4, 78507.1, 81507.3]
    for idx, d in enumerate(task.partial_distance):
        assert math.isclose(d, partial_distances[idx], abs_tol=1)

    # SS Distance Optimization:
    assert math.isclose(task.SS_distance, 73708.6, abs_tol=1)

def test_check_in_radius():
    # check in radius
    assert goal_tp.in_radius(short, 0, 0) is True
    assert goal_tp.in_radius(inside, 0, 0) is True
    assert goal_tp.in_radius(after_and_out, 0, 0) is False
    assert goal_tp.in_radius(line, 0, 0) is True


def test_in_goal_sector():
    assert in_goal_sector(test_task, short) is False
    assert in_goal_sector(test_task, after_and_out) is False
    assert in_goal_sector(test_task, inside) is True
    assert in_goal_sector(test_task, line) is True
    assert in_goal_sector(test_task, meter_short_of_tolerance) is False
    assert in_goal_sector(test_task, short_but_tolerance) is True
