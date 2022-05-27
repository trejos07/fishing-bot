import uuid
from framework.behavior_tree.core.nodes.node_state import NodeState

class Node(object):
    title = None
    category = None
    description = None
    nextId = 0

    def __init__(self):
        Node.nextId += 1
        self.id =  Node.nextId #str(uuid.uuid1())
        self.title = self.title or self.__class__.__name__
        self.description = self.description or ''
        self.parameters = {}
        self.properties = {}

    @property
    def name(self):
        return self.__class__.__name__

    def _execute(self, tick):
        self._enter(tick)

        if (not tick.blackboard.get('is_open', tick.tree.id, self.id)):
            self._open(tick)

        status = self._tick(tick)

        if (status != NodeState.RUNNING):
            self._close(tick)

        self._exit(tick)

        return status

    def _enter(self, tick):
        tick._enter_node(self)
        self.enter(tick)

    def _open(self, tick):
        tick._open_node(self)
        tick.blackboard.set('is_open', True, tick.tree.id, self.id)
        self.open(tick)

    def _tick(self, tick):
        tick._tick_node(self)
        return self.tick(tick)

    def _close(self, tick):
        tick._close_node(self)
        tick.blackboard.set('is_open', False, tick.tree.id, self.id)
        self.close(tick)

    def _exit(self, tick):
        tick._exit_node(self)
        self.exit(tick)

    def enter(self, tick): pass
    def open(self, tick): pass
    def tick(self, tick): pass
    def close(self, tick): pass
    def exit(self, tick): pass