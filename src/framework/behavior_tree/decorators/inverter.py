from framework.behavior_tree.core.nodes.decorator import Decorator
from framework.behavior_tree.core.nodes.node_state import NodeState

__all__ = ['Inverter']

class Inverter(Decorator):
    def tick(self, tick):
        if not self.child:
            return NodeState.ERROR

        status = self.child._execute(tick)

        if status == NodeState.SUCCESS:
            status = NodeState.FAILURE
        elif status == NodeState.FAILURE:
            status = NodeState.SUCCESS

        return status
        
