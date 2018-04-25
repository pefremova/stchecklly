from functools import partial

from future.utils import viewitems, viewkeys, viewvalues, with_metaclass

from .actions import get_wrong_transitions, get_correct_transitions, load_from_csv, get_random_obj_in_state


class STMeta(type):

    def __new__(mcs, name, bases, dct):
        cls = super(STMeta, mcs).__new__(mcs, name, bases, dct)

        def get_all_test_names():
            names = list(cls.__dict__.keys())
            for base in bases:
                names.extend(base.__dict__.keys())
            return [re.sub('_negative|_positive', '', k) for k in set(names) if k.startswith('test_')]

        def get_test_name(state, action):
            return "test_DO_%s_IN_%s" % (action.name, state.name)

        all_test_names = get_all_test_names()
        for state, action in getattr(cls, 'get_wrong_transitions')():
            test_name = get_test_name(state, action)
            new_func = partial(cls._test_negative, state=state, action=action)
            new_func.__doc__ = cls._test_negative.__doc__
            if test_name not in all_test_names:
                setattr(cls, test_name + '_negative', new_func)

        for state, action, new_state in getattr(cls, 'get_correct_transitions')():
            test_name = get_test_name(state, action)
            new_func = partial(cls._test_positive, state=state, action=action, new_state=new_state)
            new_func.__doc__ = cls._test_positive.__doc__
            if test_name not in all_test_names:
                setattr(cls, test_name + '_positive', new_func)

        return cls


class StateTransitionsMixIn(with_metaclass(STMeta, object)):

    actions = None
    config = None
    csv_path = None
    transitions_negative = ()
    transitions_negative_exclude_states = ()
    transitions_negative_exclude_actions = ()
    transitions_positive = ()
    transitions_positive_exclude_states = ()
    transitions_positive_exclude_actions = ()

    @classmethod
    def get_actions(cls):
        if cls.actions:
            return cls.actions
        if cls.csv_path:
            cls.actions, _ = load_from_csv(cls.csv_path, cls.config)
            return cls.actions
        return {}

    @classmethod
    def get_correct_transitions(cls):
        return cls.transitions_positive or get_correct_transitions(cls.get_actions(),
                                                                   exclude_states=cls.transitions_positive_exclude_states,
                                                                   exclude_actions=cls.transitions_positive_exclude_actions)

    @classmethod
    def get_wrong_transitions(cls):
        return cls.transitions_negative or get_wrong_transitions(cls.get_actions(),
                                                                 exclude_states=cls.transitions_negative_exclude_states,
                                                                 exclude_actions=cls.transitions_negative_exclude_actions)

    def _test_negative(self, state, action):
        data = self.deepcopy(self.state_data)
        additional = self.deepcopy(self.state_additional_data)
        obj = get_random_obj_in_state(self.actions, state, data, **additional)
        data['obj_pk'] = obj.pk
        try:
            action.do(data)
            state.check(data)
        except Exception:
            self.errors_append()

    def _test_positive(self, state, action, new_state):
        data = self.deepcopy(self.state_data)
        additional = self.deepcopy(self.state_additional_data)
        obj = get_random_obj_in_state(self.actions, state, data, **additional)
        data['obj_pk'] = obj.pk
        try:
            action.do(data)
            new_state.check(data)
        except Exception:
            self.errors_append()
