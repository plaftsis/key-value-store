class Node:

    def __init__(self):
        self.value = None
        self.children = {}


class Trie(object):

    def __init__(self):
        self.root = Node()

    def insert(self, node, key, value):
        exists = True
        for char in key:
            if char not in node.children:
                node.children[char] = Node()
                exists = False
            node = node.children[char]
        if not exists or (exists and node.value is None):
            node.value = value
            if isinstance(value, dict):
                for k, v in value.items():
                    self.insert(node, '.{}'.format(k), v)
            return True
        elif not exists:
            return False

    def find(self, key):
        node = self.root
        for char in key:
            if char in node.children:
                node = node.children[char]
            else:
                return None
        return node.value

    def delete(self, key):
        def _delete(node, key, d):
            if d == len(key):
                node.value = None
            else:
                c = key[d]
                if c in node.children and _delete(node.children[c], key, d + 1):
                    del node.children[c]
            return node.value is None and len(node.children) == 0

        if self.find(key) is not None:
            _delete(self.root, key, 0)
            return True
        else:
            return False
