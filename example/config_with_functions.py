def create(data):
    print('Do create with %s' % data)


def delete(data):
    print('Do delete with %s' % data)


def approve(data):
    print('Do approve with %s' % data)


ACTIONS = {None: {create: 'created'},
           'created': {approve: 'approve',
                       delete: 'deleted'},
           'deleted': {}}

START_STATE = None
