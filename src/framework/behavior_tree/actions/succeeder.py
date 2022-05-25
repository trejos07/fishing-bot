from src.framework.behavior_tree.core.nodes.action import Action
from src.framework.behavior_tree.core.nodes.node_state import NodeState

__all__ = ['Succeeder']

class Succeeder(Action):
    def tick(self, tick):
        return NodeState.SUCCESS;