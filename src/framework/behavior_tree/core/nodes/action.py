from src.framework.behavior_tree.core.nodes.node import Node
from src.framework.behavior_tree.core.nodes.node_types import NodeType

__all__ = ['Action']


class Action(Node):
    category = NodeType.ACTION

    def __init__(self):
        super(Action, self).__init__()
        
