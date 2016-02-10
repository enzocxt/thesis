#!/usr/bin/python

# Pattern abstract class
class Pattern(object):
    def __init__(self):
        self.id = None
        self.support = None


class Edge():
    def __init__(self):
        self.id = None
        self.fromnode = None
        self.tonode = None
        self.label = None

class Node():
    def __init__(self):
        self.id = None
        self.label = None
        self.edges = []

class Graph(Pattern):
    def __init__(self, nsupport=None):
        self.id = None
        self.edges = []
        self.nodes = []
        self.nsupport = nsupport

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, edge):
        self.edges.append(edge)


class Itemset(Pattern):
    def __init__(self, itemset=None, support=None):
        #Pattern.__init__()
        self.itemset = itemset
        self.support = support

    def isValid(self):
        pass

    def isClosed(self):
        pass

class Sequence(Pattern):
    def __init__(self, sequence=None):
        Pattern.__init__()
        self.sequence = sequence