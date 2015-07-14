from darwin.potential import evidence, multiply_all, normalize
from darwin.inference.sum_out import sum_out
from darwin.inference.barren import remove_barren
from darwin.modelling.d_separation import d_separation
from darwin.utils.mn_utils import (
    propagation_path_to_node, propagation_path_from_node
)
from random import choice
import networkx as nx


class Boss:

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

        ### DEBUG
        # print()
        # print()
        # print("=============> Message from {} to {} <=============".format(
        #     node_from, node_to))
        ### --- DEBUG

        # Collect assigned and incoming messages
        possibly_relevant = self._collect_assigned_incoming_potentials(
            node_from, node_to)

        # Support variables
        separator_variables = [v for v in node_from if v in node_to]
        vars_to_sum_out = [v for v in node_from
                           if v not in separator_variables]

        # Collect relevant potentials
        while True:
            run_again = False
            for potential in possibly_relevant:
                vars_in_separator = set(potential.variables).intersection(
                    set(separator_variables))
                vars_in_sum_out = set(potential.variables).intersection(
                    set(vars_to_sum_out))
                if len(vars_in_separator) > 0 and len(vars_in_sum_out) > 0:
                    ### DEBUG
                    # print("--> Potential {} with {} in separator and {} in sum out <====".format(
                    #     potential, vars_in_separator, vars_in_sum_out))
                    ### --- DEBUG
                    possibly_relevant = sum_out(
                        vars_in_sum_out,
                        possibly_relevant,
                        is_to_remove_barren=True)
                    run_again = True
                    break
            if not run_again:
                break

        ### DEBUG
        # print("++> Relevant")
        # for p in possibly_relevant:
        #     print("++> All v in separator: {}".format(all([v in separator_variables for v in p.variables
        #                                                     if len(p.variables) > 0])))
        #     print(p)
        ### --- DEBUG

        # Messages: all potentials with all variables in the separator
        messages = [p for p in possibly_relevant
                    if all([v in separator_variables for v in p.variables
                            if len(p.variables) > 0])]

        ### DEBUG
        # print("++> Final Messages:")
        # for p in messages:
        #     print(p)
        # print()
        # print()
        ### --- DEBUG

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

        ### DEBUG
        # print("**> Assigned potentials in {}:".format(node))
        # for p in collection:
        #     print(p)
        # ### DEBUG
        # print("**> Incoming potentials to {}:".format(node))
        ### --- DEBUG

        for neighbor in nx.all_neighbors(self.join_tree, node):
            if except_node and neighbor == except_node:
                continue
            incoming_messages = self.separators[(neighbor, node)]
            ### DEBUG
            # print(">> From neighbor {}:".format(neighbor))
            # for p in incoming_messages:
            #     print(p)
            ### --- DEBUG
            collection.extend(incoming_messages)

        return collection
