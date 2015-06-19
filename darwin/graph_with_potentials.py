import networkx as nx


class GraphWithPotentials:

    def __init__(self):
        self.potentials = []
        self.graph = nx.Graph()
        # a map from each node to a list
        # of assigned potentials.
        self.assignments = {}

    def add_potential(self, node, potential):
        self.potentials.append(potential)
        if node in self.assignments:
            self.assignments[node].append(potential)
        else:
            self.assignments[node] = [potential]

    def add_graph(self, graph):
        self.graph = graph

    def get_potentials(self, node):
        return self.assignments[node]
