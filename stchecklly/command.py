import argparse

from stchecklly.actions import generate_lists, load_config, prepare_actions, view_schema, load_from_csv
from stchecklly.models import Pipeline


def add_arguments(parser):
    parser.add_argument('-c', '--config', dest='config_path', help='Path to config file')
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
                        help='Show only count ')


def _main(**kwargs):
    if not kwargs.get('config_path') and not kwargs.get('csv_path'):
        exit('one of config_path or csv_path are required')
    if kwargs.get('csv_path'):
        ACTIONS, state_map = load_from_csv(kwargs.get('csv_path'))
    if kwargs.get('config_path'):
        config = load_config(kwargs.get('config_path'))
        if not kwargs.get('csv_path'):
            ACTIONS, state_map, action_map = prepare_actions(config.ACTIONS)

    START_STATE = state_map[config.START_STATE]

    if kwargs.get('show'):
        try:
            view_schema({str(k).replace(' ', '\n'): {str(kk).replace(' ', '\n'): str(vv).replace(' ', '\n')
                                                     for kk, vv in v.items()} for k, v in ACTIONS.items()})
            exit()
        except ImportError:
            exit('Need graphviz installed')
    lists = generate_lists(ACTIONS, start_state=START_STATE,
                           max_length=kwargs.get('max_length'), max_repeat=kwargs.get('max_repeat'))
    print('Count of lists: %s' % len(lists))
    if kwargs.get('only_count'):
        exit()
    for l in lists:
        print(l)
        if kwargs.get('verbose') > 1 or kwargs.get('test'):
            pipeline = Pipeline(ACTIONS, l, START_STATE, None)
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
