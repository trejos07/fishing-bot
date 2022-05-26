from src.framework.behavior_tree.core.nodes.node import Node
from src.framework.behavior_tree.core.nodes.node_types import NodeType

__all__ = ['Decorator']


class Decorator(Node):
    category = NodeType.DECORATOR

    def __init__(self, child=None):
        super(Decorator, self).__init__()

        self.child = child or []
