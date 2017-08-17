from copy import copy


class State(object):
    name = ''
    human_name = ''

    def __init__(self, name='', human_name='', check=None):
        super().__init__()
        self.name = self.name or name
        self.human_name = self.human_name or human_name
        if check:
            self.check = check

    def check(self, data):
        pass

    def get_text(self):
        return self.human_name or self.name

    def __repr__(self, *args, **kwargs):
        return self.get_text()


class Action(object):
    name = ''
    human_name = ''

    def __init__(self, name='', action=None, human_name=''):
        super().__init__()
        if action:
            self.do = action
        self.name = self.name or name or self.do.__name__
        self.human_name = self.human_name or human_name

    def do(self, data):
        pass

    def get_text(self):
        return self.human_name or self.name

    def __repr__(self, *args, **kwargs):
        return self.get_text()


class Pipeline(object):

    def __init__(self, config_actions, actions_list, start_state, data):
        super().__init__()
        # because deepcopy regenerate all class instances
        self.config_actions = {k: copy(v) for k, v in config_actions.items()}
        self.actions_list = actions_list
        self.start_state = start_state
        self.current_state = start_state
        self.data = data

    def get_next_state(self, current_state, action):
        return self.config_actions[current_state][action]

    def set_next_state(self, action):
        self.current_state = self.get_next_state(self.current_state, action)

    def run(self):
        for action in self.actions_list:
            action.do(self.data)
            self.set_next_state(action)
            self.current_state.check(self.data)

    def get_text(self):
        result = '*' * 20
        result += '\nstart state: {}'.format(self.start_state.get_text())
        current_state = self.start_state
        for action in self.actions_list:
            current_state = self.get_next_state(current_state, action)
            result += '\n{} (next state: {})'.format(action.get_text(), current_state.get_text())
        result += '\n' + '*' * 20
        return result
