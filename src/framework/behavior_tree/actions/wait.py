import time
from framework.behavior_tree.core.nodes.action import Action
from framework.behavior_tree.core.nodes.node_state import NodeState

__all__ = ['Wait']

class Wait(Action):

    def open(self, tick):
        end_time = time.perf_counter() + self.properties.get('time', 0)
        tick.blackboard.set('end_time', end_time, tick.tree.id, self.id)

    def tick(self, tick):

        end_time = tick.blackboard.get('end_time', tick.tree.id, self.id)
        curr_time = time.perf_counter()

        if (curr_time > end_time):
            return NodeState.SUCCESS

        return NodeState.RUNNING