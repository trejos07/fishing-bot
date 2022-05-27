import uuid
import itertools
from framework.behavior_tree.core.nodes.node_types import NodeType
from framework.behavior_tree.core.tick import Tick
from framework.behavior_tree.core.blackboard import Blackboard

__all__ = ['BehaviorTree']

class BehaviorTree(object):
    def __init__(self):
        self.id = str(uuid.uuid1())
        self.title = 'Behavior Tree'
        self.description = ''
        self.properties = {}
        self.root = None
        self.debug = None

    def load(self, data, names=None):
        names = names or {}
        self.title = data['title'] or self.title
        self.description = data['description'] or self.description
        self.properties = data['properties'] or self.properties

        nodes = {}
        for key in data['nodes']:
            spec = data['nodes'][key]

            if spec['name'] in names:
                cls = names[spec['name']]

            elif hasattr(NodeType, spec['name']):
                cls = getattr(NodeType, spec['name'])

            else:
                raise AttributeError('BehaviorTree.load: Invalid node name "%s"'%spec['name'])

            node = cls()
            node.id = spec['id'] or node.id
            node.title = spec['title'] or node.title
            node.description = spec['description'] or node.description
            node.properties = spec['properties'] or node.properties
            nodes[key] = node

        for key in data['nodes']:
            spec  = data['nodes'][key]
            node = nodes[key]
            
            if node.category == NodeType.COMPOSITE and 'children' in spec:
                for cid in spec['children']:
                    node.children.append(nodes[cid])

            elif node.category == NodeType.DECORATOR and 'child' in spec:
                node.child = nodes[spec['child']]

        if (data['root']):
            self.root = nodes[data['root']];


    def dump(self):
        data = {}
        custom_names = []

        data['title'] = self.title
        data['description'] = self.description
        data['root'] = self.root.id if self.root else None
        data['properties'] = self.properties
        data['nodes'] = {}
        data['custom_nodes'] = []

        if not self.root:
            return data

        stack = [self.root]
        while len(stack) > 0:
            node = stack.pop()
            spec = {}
            spec['id'] = node.id
            spec['name'] = node.name
            spec['title'] = node.title
            spec['description'] = node.description
            spec['properties'] = node.properties

            name = node.__class__.__name__
            if not hasattr(NodeType, name) and name not in custom_names:
                sub_data = {}
                sub_data['name'] = name
                sub_data['title'] = node.title
                sub_data['category'] = node.category

                custom_names.append(name)
                data['custom_nodes'].append(sub_data)

            if node.category == NodeType.COMPOSITE and hasattr(node, 'children'):
                children = []
                for c in reversed(node.children):
                    children.append(c.id)
                    stack.append(c)
                spec['children'] = children
            elif node.category == NodeType.DECORATOR and hasattr(node, 'child'):
                stack.append(node.child)
                spec['child'] = node.child.id

            data['nodes'][node.id] = spec

        return data


    def tick(self, target, blackboard : Blackboard):

        # Create the TICK object
        tick = Tick()
        tick.target = target
        tick.blackboard = blackboard
        tick.tree = self
        tick.debug = self.debug

        # Tick node
        state = self.root._execute(tick)

        # # Close node from last tick, if needed
        # last_open_nodes = blackboard.get('open_nodes', self.id)
        # curr_open_nodes = tick._open_nodes

        # start = 0
        # for node1, node2 in zip(last_open_nodes, curr_open_nodes):
        #     start += 1
        #     if node1 != node2:
        #         break

        # # - close nodes
        # for i in range(len(last_open_nodes)-1, start-1, -1):
        #     last_open_nodes[i]._close(tick);

        # Populate blackboard
        blackboard.set('open_nodes', tick._open_nodes, self.id)
        blackboard.set('node_count', tick._node_count, self.id)