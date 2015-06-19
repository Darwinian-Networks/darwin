from darwin.graph_with_potentials import GraphWithPotentials
from darwin.utils.bn_utils import moral_graph, junction_tree
from darwin.markov_network import MarkovNetwork


class BayesianNetwork(GraphWithPotentials):

    def get_potential(self, node):
        return self.get_potentials(node)[0]

    def get_markov_network(self):

        mn = MarkovNetwork()

        # 1) Graph transformation:
        # moralization
        graph = moral_graph(self.graph)
        # build join tree
        join_tree = junction_tree(graph)
        mn.add_graph(join_tree)

        # 2) Probability tables:
        for potential in self.potentials:
            for node in mn.graph.nodes():
                if set(potential.variables).issubset(set(node)):
                    mn.add_potential(node, potential)

        return mn
