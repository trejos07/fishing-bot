__all__ = ['Error']

from framework.behavior_tree.core.nodes.action import Action
from framework.behavior_tree.core.nodes.node_state import NodeState

class Error(Action):
    def tick(self, tick):
        return NodeState.ERROR;