# CREDITS: https://github.com/pgmpy/pgmpy/blob/dev/pgmpy/models/MarkovModel.py
import networkx as nx
import itertools as it
from functools import reduce
from operator import mul


def moralize(graph):
    directed_graph = graph.copy()
    edges_to_add = []
    for node in directed_graph.nodes():
        parents = directed_graph.predecessors(node)
        if len(parents) > 1:
            edges_to_add.extend([couple
                                 for couple in it.combinations(parents, 2)])
    directed_graph.add_edges_from(edges_to_add)
    directed_graph = directed_graph.to_undirected()
    return directed_graph


def build_join_tree(moralized_graph, cardinalities):

    # Triangulate the graph to make it chordal
    triangulated_graph = triangulate(moralized_graph, cardinalities)

    # Find maximal cliques in the chordal graph
    cliques = list(map(tuple, nx.find_cliques(triangulated_graph)))

    # If there is only 1 clique, then the junction tree formed is just a
    # clique tree with that single clique as the node
    clique_trees = None
    if len(cliques) == 1:
        clique_trees = nx.Graph()
        clique_trees.add_node(cliques[0])

    # Else if the number of cliques is more than 1 then create a complete
    # graph with all the cliques as nodes and weight of the edges being
    # the length of sepset between two cliques
    elif len(cliques) >= 2:
        complete_graph = nx.Graph()
        edges = list(it.combinations(cliques, 2))
        weights = list(map(lambda x: len(set(x[0]).intersection(set(x[1]))),
                       edges))
        for edge, weight in zip(edges, weights):
            complete_graph.add_edge(*edge, weight=-weight)

        # Create clique trees by minimum (or maximum) spanning tree method
        clique_trees = nx.Graph(
            nx.minimum_spanning_tree(complete_graph).edges()
            )

    return clique_trees


def triangulate(moralized_graph, cardinalities,
                heuristic='H6', order=None, inplace=False):

    graph_copy = nx.Graph(moralized_graph.edges())
    edge_set = set()

    def _find_common_cliques(cliques_list):
        """
        Finds the common cliques among the given set of cliques for
        corresponding node.
        """
        common = set([tuple(x) for x in cliques_list[0]])
        for i in range(1, len(cliques_list)):
            common = common & set([tuple(x) for x in cliques_list[i]])
        return list(common)

    def _find_size_of_clique(clique, cardinalities):
        """
        Computes the size of a clique.
        Size of a clique is defined as product of cardinalities of all the
        nodes present in the clique.
        """
        return list(map(lambda x: reduce(mul, [cardinalities[node]
                                               for node in x], 1),
                        clique))

    def _get_cliques_dict(node):
        """
        Returns a dictionary in the form of {node: cliques_formed} of the
        node along with its neighboring nodes.
        clique_dict_removed would be containing the cliques created
        after deletion of the node
        clique_dict_node would be containing the cliques created before
        deletion of the node
        """
        graph_working_copy = nx.Graph(graph_copy.edges())
        neighbors = graph_working_copy.neighbors(node)
        graph_working_copy.add_edges_from(it.combinations(neighbors, 2))
        clique_dict = nx.cliques_containing_node(graph_working_copy,
                                                 nodes=([node] + neighbors))
        graph_working_copy.remove_node(node)
        clique_dict_removed = nx.cliques_containing_node(graph_working_copy,
                                                         nodes=neighbors)
        return clique_dict, clique_dict_removed

    if not order:

        order = []

        for index in range(len(moralized_graph.nodes())):
            # S represents the size of clique created by deleting the
            # node from the graph
            S = {}
            # M represents the size of maximum size of cliques given by
            # the node and its adjacent node
            M = {}
            # C represents the sum of size of the cliques created by the
            # node and its adjacent node
            C = {}
            for node in set(graph_copy.nodes()) - set(order):
                clique_dict, clique_dict_removed = _get_cliques_dict(node)
                S[node] = _find_size_of_clique(
                    _find_common_cliques(list(clique_dict_removed.values())),
                    cardinalities
                )[0]
                common_clique_size = _find_size_of_clique(
                    _find_common_cliques(list(clique_dict.values())),
                    cardinalities
                )
                M[node] = max(common_clique_size)
                C[node] = sum(common_clique_size)

            if heuristic == 'H1':
                node_to_delete = min(S, key=S.get)

            elif heuristic == 'H2':
                S_by_E = {key: S[key] / cardinalities[key] for key in S}
                node_to_delete = min(S_by_E, key=S_by_E.get)

            elif heuristic == 'H3':
                S_minus_M = {key: S[key] - M[key] for key in S}
                node_to_delete = min(S_minus_M, key=S_minus_M.get)

            elif heuristic == 'H4':
                S_minus_C = {key: S[key] - C[key] for key in S}
                node_to_delete = min(S_minus_C, key=S_minus_C.get)

            elif heuristic == 'H5':
                S_by_M = {key: S[key] / M[key] for key in S}
                node_to_delete = min(S_by_M, key=S_by_M.get)

            else:
                S_by_C = {key: S[key] / C[key] for key in S}
                node_to_delete = min(S_by_C, key=S_by_C.get)

            order.append(node_to_delete)

    graph_copy = nx.Graph(moralized_graph.edges())
    for node in order:
        for edge in it.combinations(graph_copy.neighbors(node), 2):
            graph_copy.add_edge(edge[0], edge[1])
            edge_set.add(edge)
        graph_copy.remove_node(node)

    graph_copy = nx.Graph(moralized_graph.edges())
    for edge in edge_set:
        graph_copy.add_edge(edge[0], edge[1])

    if not nx.is_chordal(graph_copy):
        print("Error when triangulating")
        return

    return graph_copy
