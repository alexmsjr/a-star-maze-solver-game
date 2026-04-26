from NPnode import NPnode

class Pnode(NPnode):
    def __init__(self, parent=None, state=None, v1=None,
                 previous=None, following=None, v2=None):
        super().__init__(parent, state, v1, previous, following)
        self.v1 = v1
        self.v2 = v2



