from framework.behavior_tree.core.nodes.node import Node
from framework.behavior_tree.core.nodes.node_types import NodeType

__all__ = ['Composite']

class Composite(Node):
    category = NodeType.COMPOSITE

    def __init__(self, children=None):
        super(Composite, self).__init__()

        self.children = children or []
