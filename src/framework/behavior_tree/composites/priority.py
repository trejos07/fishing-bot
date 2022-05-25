from src.framework.behavior_tree.core.nodes.composite import Composite
from src.framework.behavior_tree.core.nodes.node_state import NodeState

__all__ = ['Priority']

class Priority(Composite):
    def __init__(self, children=None):
        super(Priority, self).__init__(children)

    def tick(self, tick):
        for node in self.children:
            status = node._execute(tick)

            if status != NodeState.FAILURE:
                return status

        return NodeState.FAILURE
