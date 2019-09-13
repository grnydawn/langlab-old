# -*- coding: utf-8 -*-
"""ast module."""

from __future__ import unicode_literals

import treelib
from collections import OrderedDict

class Tree(treelib.Tree):
    "Syntax tree"

    def __init__(self, parsed, proxy):

        self.node_class = Node
        self._nodes = OrderedDict()
        self.root = None

        #super(Tree, self).__init__(**kwargs)

        self.parsed = parsed
        self.proxy  = proxy

        root = proxy.get_rootnode(parsed)
        tag = proxy.get_nodename(root)
        ident = proxy.get_nodeid(root)

        self.create_node(tag, ident, parent=None, data=root)

        self._create_subnodes(self[ident])

    def _create_subnodes(self, parent):

        for child in self.proxy.get_subnodes(parent.data):
            tag = self.proxy.get_nodename(child)
            ident = self.proxy.get_nodeid(child)

            self.create_node(tag, ident, parent=parent, data=child)
            self._create_subnodes(self[ident])

    def show(self, key=False, reverse=False, **kwargs):
        super(Tree, self).show(key=key, reverse=reverse, **kwargs)

    def tosource(self, stream=None):

        return self.proxy.get_source(self[self.root].data)

    def __eq__(self, other):

        n1 = self[self.root].data
        n2 = other[other.root].data

        return self.proxy.is_equivalent(n1, n2)


class Node(treelib.Node):
    "Syntax node"

    pass


class Proxy(object):

    def get_rootnode(self, tree):
        raise NotImplementedError("'%s' should implement 'get_rootnode' method!"
                                  % self.__class__.__name__)

    def get_nodename(self, node):
        raise NotImplementedError("'%s' should implement 'get_nodename' method!"
                                  % self.__class__.__name__)

    def get_nodeid(self, node):
        raise NotImplementedError("'%s' should implement 'get_nodeid' method!"
                                  % self.__class__.__name__)

    def get_subnodes(self, node):
        raise NotImplementedError("'%s' should implement 'get_subnodes' method!"
                                  % self.__class__.__name__)

    def get_source(self, node):
        raise NotImplementedError("'%s' should implement 'get_source' method!"
                                  % self.__class__.__name__)

    def is_equivalent(self, node1, node2):
        raise NotImplementedError("'%s' should implement 'is_equivalent' method!"
                                  % self.__class__.__name__)

def toast(tree, proxy):

    return Tree(tree, proxy)
