from framework.behavior_tree.core.nodes.composite import Composite
from framework.behavior_tree.core.nodes.node_state import NodeState

__all__ = ['Sequence']

class Sequence(Composite):

    def __init__(self, children=None):
        super(Sequence, self).__init__(children)

    def tick(self, tick):
        for node in self.children:
            status = node._execute(tick)

            if status != NodeState.SUCCESS:
                return status

        return NodeState.SUCCESS
