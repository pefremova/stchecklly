from stchecklly.models import State, Action
created = State('created')


def create(data):
    print('Do create with %s' % data)
create_action = Action('Delete action name', create)


def delete(data):
    print('Do delete with %s' % data)

delete_action = Action('Delete action name', delete)


def approve(data):
    print('Do approve with %s' % data)
approve_action = Action('Delete action name', approve)


ACTIONS = {None: {create_action: created},
           created: {approve_action: 'approve',
                     delete_action: 'deleted'},
           'deleted': {}}

START_STATE = None
