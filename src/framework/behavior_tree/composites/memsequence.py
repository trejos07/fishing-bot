from framework.behavior_tree.core.nodes.composite import Composite
from framework.behavior_tree.core.nodes.node_state import NodeState

__all__ = ['MemSequence']

class MemSequence(Composite):
    def __init__(self, children=None):
        super(MemSequence, self).__init__(children)

    def open(self, tick):
        tick.blackboard.set('running_child', 0, tick.tree.id, self.id)

    def tick(self, tick):
        idx = tick.blackboard.get('running_child', tick.tree.id, self.id)

        for i in range(idx, len(self.children)):
            node = self.children[i]
            status = node._execute(tick)

            if status != NodeState.SUCCESS:
                if status == NodeState.RUNNING:
                    tick.blackboard.set('running_child', i, tick.tree.id, self.id)
                return status

        return NodeState.SUCCESS
