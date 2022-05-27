import time
from framework.behavior_tree.core.behavior_tree import BehaviorTree
from framework.behavior_tree.composites.sequence import Sequence
from framework.behavior_tree.core.nodes.action import Action
from framework.behavior_tree.core.blackboard import Blackboard
from framework.behavior_tree.actions.logger import Logger
from framework.behavior_tree.actions.wait import Wait

behavior_tree_data = {
    'title': 'Behavior Tree',
    'description': '',
    'properties': {},
    'root': '1',
    'nodes': {
        '1': {
            'id': '1',
            'name': 'Sequence',
            'title': 'Sequence',
            'description': '',
            'properties': {},
            'children': ['2', '3', '4']
        },
        '2': {
            'id': '2',
            'name': 'Logger',
            'title': 'Logger 1',
            'description': '',
            'properties': {
                'message': 'Hello'
            }
        },
        '3': {
            'id': '3',
            'name': 'Logger',
            'title': 'Logger 2',
            'description': '',
            'properties': {
                'message': 'World'
            }
        },
        '4': {
            'id': '4',
            'name': 'Wait',
            'title': 'Wait',
            'description': '',
            'properties': {
                'time': 10
            }
        }

    }
}

valid_nodes = {
    'Sequence': Sequence,
    "Action": Action,
    "Logger": Logger,
    "Wait": Wait
}

def main ():
    tree = BehaviorTree()
    blackboard = Blackboard()
    target = None
    tree.load(behavior_tree_data, valid_nodes)

    while True:
        tree.tick(target, blackboard)
        time.sleep(0.5)


if __name__ == "__main__":
    main()