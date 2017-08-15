from stchecklly.models import State, Action
created = State('created')


def create(data):
    print('Do create with %s' % data)


def delete(data):
    print('Do delete with %s' % data)

delete_action = Action(delete, 'Delete action name')


def approve(data):
    print('Do approve with %s' % data)


ACTIONS = {None: {create: created},
           created: {approve: 'approve',
                     delete_action: 'deleted'},
           'deleted': {}}

START_STATE = None
