import time
import random
import itertools
from itertools import islice
from collections import namedtuple
import os

import click

from cls.parsers import parsing
from cls.optimizations import distribution
from cls.optimizations import compression 


ALGORITHMS = {
    'pbd': distribution.palette_pbd,
    'cbd': distribution.palette_cbd,
    'obs': distribution.one_big_switch,
    'bm' : distribution.boolean_minimization,
    'bit': distribution.one_bit
}

GlobalParams = namedtuple(
    'GlobalParams', ['name', 'num_lines', 'classbench_lines', 'algo'])
GLOBAL_PARAMS = GlobalParams(None, None, None, 'all')

BINSEARCH_THRESHOLD = 5

def _save(num_rules, max_capacity, path_length, algo_name, result, time):
    with open('out.tsv', 'a') as f:
        print(os.path.basename(GLOBAL_PARAMS.name), num_rules,
              max_capacity, path_length, algo_name, result, time,
              sep='\t', file=f)


def _evaluate(result, classifier):
    if result is None:
        return None
    return (sum(result) - len(classifier)) / len(classifier)


def _load_classifier(num_lines):
    random.seed(12)

    if num_lines is not None:
        lines = random.sample(GLOBAL_PARAMS.classbench_lines, num_lines)
    else:
        lines = GLOBAL_PARAMS.classbench_lines

    classifier = parsing.read_classifier(parsing.classbench_ips, lines)
    return compression.try_boolean_minimization(classifier)


def _run(classifier, max_capacity, length, algo_name):
    print("running {} on a clsfier with {:d} rules: max_capacity = {:d}, length = {:d}"
          .format(algo_name, len(classifier), max_capacity, length))


    start_time = time.time()
    result = ALGORITHMS[algo_name](classifier, [max_capacity] * length)
    end_time = time.time()

    _save(len(classifier), max_capacity, length, algo_name, 
          _evaluate(result, classifier), end_time - start_time)

    return result


@click.group()
@click.option('--algo', multiple=True, type=click.Choice(list(ALGORITHMS)))
@click.argument('classbench-input', type=click.File("r"))
def common(algo, classbench_input):
    if len(algo) == 0:
        algo = list(ALGORITHMS)
    else:
        algo = list({ alg : ALGORITHMS[alg] for alg in algo })
    global GLOBAL_PARAMS
    GLOBAL_PARAMS = GlobalParams(
        classbench_input.name, num_lines, list(classbench_input), algo)


@common.command()
@click.option('--num-lines', default=None, type=int)
@click.option('--capacity', required=True, type=int)
@click.option('--length', required=True, type=int)
def single(num_lines, capacity, length):
    classifier = _load_classifier(num_lines)
    for algo in GLOBAL_PARAMS.algo:
        _run(classifier, capacity, length, algo)


@common.command()
@click.option('--num-lines', default=None, type=int)
@click.option('--start', required=True, type=int)
@click.option('--end', required=True, type=int)
@click.option('--step', default=1, type=int)
@click.option('--length', required=True, type=int)
def capacity(num_lines, start, end, step, length):
    classifier = _load_classifier(num_lines)
    for algo in GLOBAL_PARAMS.algo:
        if step > 0:
            for capacity in range(start, end + 1, step):
                _run(classifier, capacity, length, algo)
        elif step == -1:
            capacity = start
            while capacity < end:
                _run(classifier, capacity, length, algo)
                capacity = capacity * 2
        elif step == -2:
            lo, hi = start, end
            while hi - lo > BINSEARCH_THRESHOLD:
                capacity = int((lo + hi) / 2)
                result = _run(classifier, capacity, length, algo)
                if result is None:
                    lo = capacity
                else:
                    hi = capacity


@common.command()
@click.option('--num-lines', default=None, type=int)
@click.option('--start', required=True, type=int)
@click.option('--end', required=True, type=int)
@click.option('--step', default=1, type=int)
@click.option('--capacity', required=True, type=int)
def length(num_lines, start, end, step, capacity):
    classifier = _load_classifier(num_lines)
    for algo in GLOBAL_PARAMS.algo:
        for length in range(start, end + 1, step):
            _run(classifier, capacity, length, algo)

@common.command()
@click.option('--start', required=True, type=int)
@click.option('--end', required=True, type=int)
@click.option('--step', default=1, type=int)
@click.option('--capacity', required=True, type=int)
@click.option('--length', required=True, type=int)
def num_lines(start, end, step, capacity, length):
    for num_lines in range(start, end + 1, step):
        classifier = _load_classifier(num_lines)
        for algo in GLOBAL_PARAMS.algo:
            _run(classifier, capacity, length, algo)

if __name__ == '__main__':
    common()
