from darwin.potential import evidence, multiply_all, normalize
from darwin.inference.sum_out import sum_out
from darwin.modelling.d_separation import d_separation
from darwin.utils.mn_utils import (
    propagation_path_to_node, propagation_path_from_node
)
from random import choice
import networkx as nx


class LazyPropagation:

    def __init__(self, bn):
        self.dag = bn.graph
        # Lazy needs the BN for testing independencies,
        # but perform propagation in a MN
        mn = bn.get_markov_network()
        self.markov_network = mn
        self.join_tree = mn.graph
        # save evidences observed
        self.evidence = {}

    def propagate(self, evidence_observed=None):

        # 0) Initialize assigned potentials and separators
        self.assignments = {k: self.markov_network.assignments[k]
                            for k in self.markov_network.assignments}
        self.separators = {}
        for e in self.markov_network.graph.edges():
            self.separators[e] = []
            self.separators[tuple(reversed(e))] = []

        # 1) Select root
        root = choice(list(self.assignments.keys()))

        # 2) Entering evidence
        if evidence_observed:
            for node in self.assignments:
                self.assignments[node] = evidence(
                    self.assignments[node], evidence_observed)
                self.evidence = evidence_observed

        # 3) Perform Inward Pass
        inward_path = propagation_path_to_node(root, self.join_tree)
        for edge in inward_path:
            self.send_message(edge[0], edge[1])

        # 4) Perform Outward Pass
        outward_path = propagation_path_from_node(
            root, self.join_tree)
        for edge in outward_path:
            self.send_message(edge[0], edge[1])

    def send_message(self, node_from, node_to):

        # Collect assigned and incoming messages
        possibly_relevant = self._collect_assigned_incoming_potentials(
            node_from, node_to)

        # Support variables
        separator_variables = [v for v in node_from if v in node_to]
        vars_to_sum_out = [v for v in node_from
                           if v not in separator_variables]

        # Delete independent potentials
        evidence_variables = list(self.evidence.keys())
        for potential in list(possibly_relevant):
            X = potential.variables
            Y = evidence_variables
            Z = separator_variables
            if d_separation(X, Y, Z, self.dag):
                possibly_relevant.remove(potential)

        # Sum out node_from not in separator from relevant potentials
        messages = sum_out(vars_to_sum_out, possibly_relevant,
                           is_to_remove_barren=True)

        # Send message by attaching it to respective separator
        self.separators[(node_from, node_to)].extend(messages)

    def query(self, variable):
        possible_nodes = [n for n in self.join_tree.nodes()
                          if variable in n]
        node = choice(possible_nodes)

        potentials = self._collect_assigned_incoming_potentials(node)
        sum_out_vars = [v for v in self.dag.nodes() if v != variable]
        potentials = sum_out(sum_out_vars, potentials)
        answer = multiply_all(potentials)
        answer = normalize(answer)
        return answer

    def _collect_assigned_incoming_potentials(self, node, except_node=None):
        collection = [p for p in self.assignments[node]]

        for neighbor in nx.all_neighbors(self.join_tree, node):
            if except_node and neighbor == except_node:
                continue
            incoming_messages = self.separators[(neighbor, node)]
            collection.extend(incoming_messages)

        return collection
