import argparse
from copy import deepcopy

from stchecklly.actions import (generate_lists, load_config, prepare_actions, view_schema, load_from_csv,
                                get_way, get_not_affect_state_actions)
from stchecklly.models import Pipeline, State


def add_arguments(parser):
    parser.add_argument('-c', '--config', dest='config_path', help='Path to config file')
    parser.add_argument('--config.start', dest='config_start_state', help='Name of start state')
    parser.add_argument('-f', '--csv-file', dest='csv_path', help='Path to csv with config')
    parser.add_argument('-s', dest='show', action='store_true', help='Show graph (need graphviz installed)')
    parser.add_argument('-V', dest='verbose', type=int, default=1, help='Verbosity level (default=1)')
    parser.add_argument('-l', '--max-length', dest='max_length', type=int,
                        default=3, help='Max length of transitions list')
    parser.add_argument('-r', '--max-repeat', dest='max_repeat', type=int, default=2,
                        help='Max one action count in transitions list')
    parser.add_argument('-t', '--test', dest='test', action='store_true',
                        help='Run check')
    parser.add_argument('-C', '--only-count', dest='only_count', action='store_true',
                        help='Show only count')
    parser.add_argument('--stats', dest='show_stats', action='store_true',
                        help='Show count statistic')
    parser.add_argument('-M', dest='only_max', action='store_true', help='Save only max length transitions lists')
    parser.add_argument('--only-length', dest='only_length', type=int, help='Save transitions lists only with this length')
    parser.add_argument('--way', dest='test_way', help='Actions list for test\nExample: "action1 -> action2"')
    parser.add_argument('-W', '--get-way', dest='get_way', help='Get way from state1 to state2\nExample: "state1 -> state2"')
    parser.add_argument('--not-affect', dest='find_not_affect', action='store_true', help='Find actions, that not change any state')


def _main(**kwargs):
    if not (kwargs.get('config_path') or kwargs.get('config_start_state')) and not kwargs.get('csv_path'):
        exit('one of (config_path or config_start_state) or csv_path are required')
    config = None
    if kwargs.get('config_path'):
        config = load_config(kwargs.get('config_path'))
        if not kwargs.get('csv_path'):
            ACTIONS, state_map, action_map = prepare_actions(config.ACTIONS)
    if kwargs.get('csv_path'):
        ACTIONS, state_map = load_from_csv(kwargs.get('csv_path'), config)
    if kwargs.get('get_way'):
        states = [el.strip() for el in kwargs.get('get_way').split('->')]
        state1, state2 = states
        way = get_way(ACTIONS, state_map[state1], state_map[state2])
        print('\n'.join([way_el.get_text() for way_el in way]))
        print(' -> '.join([way_el.name for way_el in way]))
        exit()

    start_state = kwargs.get('config_start_state') or getattr(config, 'START_STATE', None)
    START_STATE = start_state if isinstance(start_state, State) else state_map[start_state]

    if kwargs.get('show'):
        try:
            view_schema({str(k).replace(' ', '\n'): {str(kk).replace(' ', '\n'): str(vv).replace(' ', '\n')
                                                     for kk, vv in v.items()} for k, v in ACTIONS.items()})
            exit()
        except ImportError:
            exit('Need graphviz installed')

    if kwargs.get('test_way'):
        lists = [[getattr(config, name.strip()) for name in kwargs.get('test_way').split('->')], ]
    elif kwargs.get('find_not_affect'):
        print('This actions not change any state to other:')
        print('\n'.join([str(el) for el in get_not_affect_state_actions(ACTIONS)]))
        exit()
    else:
        lists = generate_lists(ACTIONS, start_state=START_STATE,
                               max_length=kwargs.get('max_length'), max_repeat=kwargs.get('max_repeat'),
                               current_max_length=0 if kwargs.get('only_max') else None,
                               only_length=kwargs.get('only_length'))
        print('Count of lists: %s' % len(lists))
        if kwargs.get('show_stats'):
            d = {i: 0 for i in range(1, kwargs.get('max_length') + 1)}
            for l in lists:
                d[len(l)] += 1
            print('\n'.join([':\t'.join([str(k), str(v)]) for k, v in d.items()]))
        if kwargs.get('only_count'):
            exit()
    for l in lists:
        print(l)
        if kwargs.get('verbose') > 1 or kwargs.get('test'):
            data = deepcopy(getattr(config, 'DATA', None))
            pipeline = Pipeline(ACTIONS, l, START_STATE, data)
        if kwargs.get('verbose') > 1:
            print(pipeline.get_text())
        if kwargs.get('test'):
            print('--- Run test ---')
            pipeline.run()
    exit()


def main():
    parser = argparse.ArgumentParser()
    add_arguments(parser)

    args = parser.parse_args()
    kwargs = args.__dict__

    _main(**kwargs)
