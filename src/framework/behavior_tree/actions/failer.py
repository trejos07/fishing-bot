
__all__ = ['Failer']

from src.framework.behavior_tree.core.nodes.action import Action
from src.framework.behavior_tree.core.nodes.node_state import NodeState

class Failer(Action):
    def tick(self, tick):
        return NodeState.FAILURE;