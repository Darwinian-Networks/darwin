import networkx as nx


def propagation_path_to_node(node, graph):
        def _propagate_to_node(c_i, c_j, propagation_path):
            neighbors = list(nx.all_neighbors(graph, c_j))
            if c_j in neighbors:
                neighbors.remove(c_j)
            if c_i in neighbors:
                neighbors.remove(c_i)
            for c_k in neighbors:
                _propagate_to_node(c_j, c_k, propagation_path)
            propagation_path.append((c_j, c_i))

        propagation_path = []
        for neighbor in list(nx.all_neighbors(graph, node)):
            _propagate_to_node(node, neighbor, propagation_path)

        return propagation_path


def propagation_path_from_node(node, graph):

    def _propagate_from_node(c_i, c_j, propagation_path):
        propagation_path.append((c_i, c_j))
        neighbors = list(nx.all_neighbors(graph, c_j))
        if c_i in neighbors:
            neighbors.remove(c_i)
        for c_k in neighbors:
            _propagate_from_node(c_j, c_k, propagation_path)

    propagation_path = []
    for neighbor in list(nx.all_neighbors(graph, node)):
        _propagate_from_node(node, neighbor, propagation_path)

    return propagation_path
