from framework.behavior_tree.core.nodes.decorator import Decorator
from framework.behavior_tree.core.nodes.node_state import NodeState

__all__ = ['Limiter']

class Limiter(Decorator):
    def __init__(self, child, max_loop):
        super(Limiter, self).__init__(child)

        self.max_loop = max_loop

    def open(self, tick):
        tick.blackboard.set('i', 0, tick.tree.id, self.id)

    def tick(self, tick):
        if not self.child:
            return NodeState.ERROR

        i = tick.blackboard.get('i', tick.tree.id, self.id)
        if i < self.max_loop:
            status = self.child._execute(tick)

            if status == NodeState.SUCCESS or status == NodeState.FAILURE:
                tick.blackboard.set('i', i+1, tick.tree.id, self.id)

            return status

        return NodeState.FAILURE
        
