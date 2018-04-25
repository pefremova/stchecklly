from copy import copy
import csv
import importlib
import os
import sys

from stchecklly.models import State, Action
from random import choice, sample


def _generate_lists(actions, start_state, previous_steps, max_l, max_repeat, current_max_length=None, only_length=None):
    is_latest = False
    if previous_steps is None:
        previous_steps = []
    if current_max_length is not None and only_length is None:
        current_max_length = max(current_max_length, len(previous_steps))
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
        if only_length:
            return [] if len(previous_steps) != only_length else [previous_steps, ], True
        return [] if current_max_length and len(previous_steps) < current_max_length else [previous_steps, ], True
    for v, new_ in current_state_actions.items():
        is_latest = False
        _result = [previous_steps + [v], ]
        if len(_result[0]) < max_l and not is_latest:
            _result, is_latest = _generate_lists(actions, new_, _result[0], max_l, max_repeat,
                                                 current_max_length=current_max_length, only_length=only_length)
            if only_length and _result:
                _result = filter(lambda el: len(el) == only_length, _result)
        elif only_length:
            _result = filter(lambda el: len(el) == only_length, _result)

        if current_max_length is not None:
            _current_max_length = len(max(_result + ['', ], key=len))
            if _current_max_length < current_max_length:
                continue
            elif _current_max_length > current_max_length:
                current_max_length = _current_max_length
                result = []
        if only_length and is_latest:
            _result = filter(lambda el: len(el) == only_length, _result)

        result.extend(_result)

    if current_max_length:
        result = list(filter(lambda el: len(el) >= current_max_length, result))
    return result, False


def generate_lists(actions, start_state, max_length=3, max_repeat=2, current_max_length=None, only_length=None):
    result, _ = _generate_lists(actions=actions,
                                start_state=start_state,
                                previous_steps=None,
                                max_l=max_length,
                                max_repeat=max_repeat,
                                current_max_length=current_max_length,
                                only_length=only_length)
    return result


def load_config(path):
    filename = os.path.splitext(os.path.basename(path))[0]
    sys.path.append(os.path.dirname(os.path.expanduser(path)))
    return importlib.import_module(filename)


def load_from_csv(path, config=None):
    result = []
    with open(path, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            result.append(row)
    state_column_count = 2 if result[0][1] == '' else 1
    action_row_count = 1
    raw_actions = result[0][state_column_count:]
    if result[1][0] == '':
        raw_actions = zip(raw_actions, result[1][state_column_count:])
        action_row_count = 2
    actions = [getattr(config, el[0], None) or Action(*el) for el in raw_actions]

    states = []
    state_map = {}
    for row in result[action_row_count:]:
        el = row[:state_column_count]
        state = getattr(config, el[0], None) or State(*el)
        states.append(state)
        state_map[el[0]] = state
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


def find_shortest_path(actions, start, end, path=[]):
    graph = {k: v.keys() for k, v in actions.items()}
    path = path + [start]
    if start == end:
        return path
    if not start in graph.keys():
        return None
    shortest = None
    for node in graph[start]:
        newpath = None
        if node not in path:
            newpath = find_shortest_path(actions, node, end, path)
        if newpath:
            if not shortest or len(newpath) < len(shortest):
                shortest = newpath
    return shortest


def get_way(ACTIONS, start_state, end_state):
    actions = {state: {v: k for k, v in el.items()} for state, el in ACTIONS.items()}
    path = find_shortest_path(actions, start_state, end_state)
    if not path:
        return []
    way = []
    for n, el in enumerate(path[1:]):
        el_dict = actions[path[n]]
        way.append(el_dict[el])
    return way


def get_wrong_transitions(actions, exclude_states=None, exclude_actions=None):
    all_actions = set(sum([list(el.keys()) for el in actions.values()], [])).difference(exclude_actions or ())
    all_states = set(actions.keys()).difference(exclude_states or ())

    res = []
    for state in all_states:
        for action in set(all_actions).difference(actions[state].keys()):
            res.append((state, action))
    return res


def get_correct_transitions(actions, exclude_states=None, exclude_actions=None):
    res = []
    for state, values in actions.items():
        if state in (exclude_states or ()):
            continue
        for action, new_state in values.items():
            if action in (exclude_actions or ()):
                continue
            res.append((state, action, new_state))
    return res


def get_not_affect_state_actions(actions):
    actions_that_change = set()
    all_actions = set()
    for state, values in actions.items():
        for action, new_state in values.items():
            all_actions.add(action)
            if new_state != state:
                actions_that_change.add(action)

    return all_actions.difference(actions_that_change)


def get_random_obj_in_state(ACTIONS, state, data, **kwargs):
    was_in = kwargs.pop('was_in', set())

    def get_obj_directly(state):
        objs = state.get_states(**kwargs)
        if objs:
            return choice(objs)
        if objs is None:
            return
        return []
    obj = get_obj_directly(state)
    if obj or obj is None:
        return obj

    previous_states = []
    for s, v in ACTIONS.items():
        if s == state or s in was_in:
            continue
        for a, ss in v.items():
            if ss == state:
                previous_states.append((s, a))
    for prev_state, to_current_action in sample(previous_states, len(previous_states)):
        """First try get one of previous state directly"""
        obj = get_obj_directly(prev_state)

        _data = data.copy()
        if obj:
            _data['obj_pk'] = obj.pk
        if obj or obj is None:
            to_current_action.do(_data)
            obj = get_obj_directly(state)
            if obj or obj is None:
                return obj
    for prev_state, to_current_action in sample(previous_states, len(previous_states)):
        _was_in = was_in.copy()
        _was_in.add(prev_state)
        obj = get_random_obj_in_state(ACTIONS, prev_state, data, was_in=_was_in, **kwargs)
        _data = data.copy()
        if obj:
            _data['obj_pk'] = obj.pk

        if obj or obj is None:
            to_current_action.do(_data)
            obj = get_obj_directly(state)
            if obj or obj is None:
                return obj
    return []
