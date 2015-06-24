from darwin.graph_with_potentials import GraphWithPotentials
from darwin.markov_network import MarkovNetwork
from darwin.utils.bn_utils import build_join_tree, moralize


class BayesianNetwork(GraphWithPotentials):

    def get_potential(self, node):
        return self.get_potentials(node)[0]

    def get_markov_network(self):

        mn = MarkovNetwork()

        # 1) Graph transformation:
        # moralization
        moral_graph = moralize(self.graph)
        # build join tree
        join_tree = build_join_tree(moral_graph, self.get_cardinalities())
        mn.add_graph(join_tree)

        # 2) Probability tables:
        for potential in self.potentials:
            for node in mn.graph.nodes():
                if set(potential.variables).issubset(set(node)):
                    mn.add_potential(node, potential)
                    break

        # Nodes without potential has empty assignment
        for node in mn.graph.nodes():
            if node not in mn.assignments:
                mn.assignments[node] = []

        return mn
