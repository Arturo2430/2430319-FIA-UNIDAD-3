"""Scheduling must preserve one primary per key and bounded graph concurrency."""

import importlib.util
from pathlib import Path
from threading import Lock
import time


spec = importlib.util.spec_from_file_location(
    'parallel_exploration', Path(__file__).resolve().parents[1] / 'scripts/run_parallel_exploration.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def test_parallel_limit_unique_graphs_and_resume():
    keys = [(f'graph{g}', algorithm, seed) for g in range(1, 7)
            for seed in (2001, 2002) for algorithm in ('ga', 'abc')]
    active, seen, recorded = set(), set(), set()
    lock = Lock()
    peak = 0

    def run(key, cpu):
        nonlocal peak
        with lock:
            assert key not in seen
            assert key[0] not in active
            seen.add(key)
            active.add(key[0])
            peak = max(peak, len(active))
            assert len(active) <= 4
        time.sleep(.005)
        with lock:
            active.remove(key[0])
        return key

    def record(key):
        assert key not in recorded
        recorded.add(key)
        return ''

    assert runner.schedule(keys, set(), [0, 2, 4, 6], lambda: '', run, record, 7) == 'attempt_limit'
    assert len(recorded) == 7
    assert runner.schedule(keys, recorded.copy(), [0, 2, 4, 6], lambda: '', run, record) == 'complete'
    assert recorded == set(keys) == seen
    assert peak > 1


def test_pause_does_not_admit_new_work_and_drains_workers():
    keys = [(f'graph{g}', 'ga', 2001) for g in range(8)]
    recorded = []

    def record(key):
        recorded.append(key)
        return 'interrupted'

    reason = runner.schedule(keys, set(), [0, 2, 4, 6], lambda: '', lambda key, cpu: key, record)
    assert reason == 'interrupted'
    assert len(recorded) == 4
    assert len(set(recorded)) == 4


def test_paused_before_launch_starts_nothing():
    def unexpected(*args):
        raise AssertionError('A stopped session must not launch a child')

    assert runner.schedule([('graph1', 'ga', 2001)], set(), [0],
                           lambda: 'low_memory', unexpected, unexpected) == 'low_memory'
