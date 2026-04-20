class NPnode(object):
    def __init__(self, parent=None, state=None, depth=None, previous=None, following=None):
        self.parent = parent
        self.state = state
        self.depth = depth
        self.previous = previous
        self.following = following

