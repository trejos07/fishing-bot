import os
from framework.behavior_tree.core.behavior_tree import BehaviorTree
from framework.behavior_tree.core.nodes.action import Action
from framework.behavior_tree.core.blackboard import Blackboard
from framework.behavior_tree.actions.logger import Logger
from framework.behavior_tree.actions.wait import Wait
from framework.behavior_tree.composites.memsequence import MemSequence
from framework.utils import json_utils

behavior_tree_data = json_utils.load_json(os.path.join(os.getcwd(), 'tree_config.json'))

valid_nodes = {
    'sequence': MemSequence,
    "Logger": Logger,
    "wait": Wait
}

def main ():
    tree = BehaviorTree()
    blackboard = Blackboard()
    target = None
    tree.load(behavior_tree_data, valid_nodes)

    while True:
        tree.tick(target, blackboard)


if __name__ == "__main__":
    main()