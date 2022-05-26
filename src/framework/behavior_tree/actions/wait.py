import time
from framework.behavior_tree.core.nodes.action import Action
from framework.behavior_tree.core.nodes.node_state import NodeState

__all__ = ['Wait']

class Wait(Action):

    def open(self, tick):
        self.start_time = time.time()
        self.end_time = self.start_time + self.properties.get('time', 0)

    def tick(self, tick):
        curr_time = time.time()

        if (curr_time > self.end_time):
            print('time out')
            return NodeState.SUCCESS

        return NodeState.RUNNING