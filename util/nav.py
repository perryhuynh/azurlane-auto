from util.utils import Utils


class NavNode(object):

    def __init__(self, name):
        """Initializes a NavNode instance, which represents a node in the
        navigation tree.
        Args:
            name (string): name (in-game location) of the node
        """
        self.name = name
        self.connections = {}


class Nav(object):

    home = NavNode('home')

    def navigate_to(self, target):
        regions = {
            'back': Region(12, 8, 45, 30)
        }
        Utils.touch_randomly(regions[target])
