from copy import copy
import csv
import importlib
import os
import sys

from stchecklly.models import State, Action


def _generate_lists(actions, start_state, previous_steps, max_l, max_repeat):
    is_latest = False
    if previous_steps is None:
        previous_steps = []
    result = []
    current_state_actions = copy(actions.get(start_state, {}))
    keys_for_remove = []
    for action_name in current_state_actions.keys():
        if previous_steps.count(action_name) >= max_repeat:
            """if action many times already in list"""
            keys_for_remove.append(action_name)
    for el in keys_for_remove:
        current_state_actions.pop(el, None)
    if not current_state_actions:
        """no any available actions from this state"""
        return [previous_steps, ], True
    for v, new_ in current_state_actions.items():
        is_latest = False
        _result = [previous_steps + [v], ]
        if len(_result[0]) < max_l and not is_latest:
            _result, is_latest = _generate_lists(actions, new_, _result[0], max_l, max_repeat)
        result.extend(_result)
    return result, False


def generate_lists(actions, start_state, max_length=3, max_repeat=2):
    result, _ = _generate_lists(actions=actions,
                                start_state=start_state,
                                previous_steps=None,
                                max_l=max_length,
                                max_repeat=max_repeat)
    return result


def load_config(path):
    filename = os.path.splitext(os.path.basename(path))[0]
    sys.path.append(os.path.dirname(os.path.expanduser(path)))
    return importlib.import_module(filename)


def load_from_csv(path):
    result = []
    with open(path, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        result = []
        for row in reader:
            result.append(row)
    state_column_count = 2 if result[0][1] == '' else 1
    action_row_count = 1
    raw_actions = result[0][state_column_count:]
    if result[1][0] == '':
        raw_actions = zip(raw_actions, result[1][state_column_count:])
        action_row_count = 2
    actions = [Action(*el) for el in raw_actions]

    states = []
    state_map = {}
    for row in result[action_row_count:]:
        state = State(*row[:state_column_count])
        states.append(state)
        state_map[state.name] = state
    ACTIONS = {}
    for n, row in enumerate(result[action_row_count:]):
        ACTIONS[states[n]] = {actions[j]: state_map[el] for j, el in enumerate(row[state_column_count:]) if el != '-'}
    return ACTIONS, state_map


def prepare_actions(actions):
    result = {}
    action_map = {}
    state_map = {}
    for raw_state, raw_actions in actions.items():
        if raw_state not in state_map.keys():
            state_map[raw_state] = State(raw_state) if not isinstance(raw_state, State) else raw_state
        state = state_map[raw_state]
        result[state] = {}
        for raw_action, raw_new_state in raw_actions.items():
            if raw_new_state not in state_map.keys():
                state_map[raw_new_state] = State(raw_new_state) if not isinstance(
                    raw_new_state, State) else raw_new_state
            if raw_action not in action_map.keys():
                action_map[raw_action] = Action(raw_action) if not isinstance(raw_action, Action) else raw_action
            action = action_map[raw_action]
            new_state = state_map[raw_new_state]
            result[state][action] = new_state
    return result, state_map, action_map


def view_schema(d):
    import graphviz
    diagramm = graphviz.Digraph(format='svg')
    for k in d.keys():
        diagramm.node(k)
    for k, v in d.items():
        for edge, k2 in v.items():
            diagramm.edge(k, k2, label=str(edge))
    diagramm.view()
