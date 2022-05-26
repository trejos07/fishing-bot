from src.framework.behavior_tree.core.nodes.node import Node
from src.framework.behavior_tree.core.nodes.node_types import NodeType

__all__ = ['Condition']

class Condition(Node):
    category = NodeType.CONDITION

    def __init__(self):
        super(Condition, self).__init__()
        
