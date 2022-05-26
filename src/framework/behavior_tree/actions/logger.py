from framework.behavior_tree.core.nodes.action import Action
from framework.behavior_tree.core.nodes.node_state import NodeState

class Logger(Action):
    def tick(self, tick):
        print(self.properties.get('message', 'No message'))
        return NodeState.SUCCESS;