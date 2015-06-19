from darwin.inference.sum_out import sum_out
from darwin.modelling.d_separation import d_separation
from darwin.potential import multiply_all, evidence, normalize


class VariableElimination:

    def __init__(self, bn):
        self.bn = bn

    def query(self, query_variables,
              evidence_observed=None, elimination_order=None):

        if not isinstance(query_variables, list):
            query_variables = [query_variables]

        # Safe copies for removal during VE
        graph_copy = self.bn.graph.copy()
        potentials = self.bn.potentials

        # Dealing with evidence.
        if evidence_observed:
            potentials = evidence(potentials, evidence_observed)

        # Name of evidence variables
        evidence_variables = list(
            evidence_observed.keys()) if evidence_observed else []

        # Remove all barren nodes.
        barren_variables = barren(list(query_variables) + evidence_variables,
                                  graph_copy)
        graph_copy.remove_nodes_from(barren_variables)
        potentials = sum_out(barren_variables, potentials)

        # Remove all independent by evidence nodes
        independent_variables = independent(query_variables,
                                            evidence_variables, graph_copy)
        graph_copy.remove_nodes_from(independent_variables)
        potentials = sum_out(independent_variables, potentials)

        # Elimination ordering
        if elimination_order:
            elimination_order = list(
                set(elimination_order)-set(graph_copy.nodes())
                )
        else:
            elimination_order = list(
                set(graph_copy.nodes()) -
                set(query_variables) -
                set(evidence_variables)
                )

        # Perform sum out of variables
        remaining_potentials = sum_out(elimination_order, potentials)
        product = multiply_all(remaining_potentials)
        normalized = normalize(product)

        return normalized


def barren(relevant_variables, dag):
    pruned_dag = dag.copy()
    barren_variables = []
    while True:
        leaves = [leaf for leaf, degree in pruned_dag.out_degree().items()
                  if degree == 0]
        barren = [leaf for leaf in leaves
                  if leaf not in relevant_variables]
        if len(barren) > 0:
            pruned_dag.remove_nodes_from(barren)
            barren_variables.extend(barren)
        else:
            break
    return barren_variables


def independent(query_variables, evidence_variables, dag):
    test_nodes = [n for n in dag.nodes()
                  if n not in query_variables + evidence_variables]

    return [n for n in test_nodes
            if d_separation(query_variables, evidence_variables, n, dag)]
