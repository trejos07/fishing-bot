from framework.behavior_tree.core.nodes.action import Action
from framework.behavior_tree.core.nodes.node_state import NodeState

__all__ = ['Runner']

class Runner(Action):
    def tick(self, tick):
        return NodeState.RUNNING;