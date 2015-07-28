from darwin.utils.potential_operations import (
    potential_multiplication,
    potential_division,
    potential_marginalization,
    potential_select_evidence,
    potential_normalization
)


class Potential:

    def __init__(self, variables, cardinalities, values,
                 left_hand_side=[], right_hand_side=[],
                 evidence={}):

        self.variables = variables
        self.cardinalities = cardinalities
        self.values = values
        self.evidence = evidence
        self.left_hand_side = left_hand_side
        self.right_hand_side = right_hand_side

    def __str__(self):
        print_out = "p({}|{}) \n    Variables: {} \n    Evidence: {}={} \n    Values: [{}]".format(
            ",".join(self.left_hand_side),
            ",".join(self.right_hand_side),
            ",".join(self.variables),
            ",".join(list(self.evidence.keys())),
            ",".join(format(x, "d") for x in list(self.evidence.values())),
            ", ".join(format(x, ".10f") for x in self.values))
        return print_out


def multiply(phi1, phi2):
    (phi_variables, phi_cardinalities, phi_values, phi_left_hand_side,
     phi_right_hand_side, phi_evidence) \
        = potential_multiplication(phi1.variables,
                                   phi1.cardinalities,
                                   phi1.values,
                                   phi1.left_hand_side,
                                   phi1.right_hand_side,
                                   phi1.evidence,
                                   phi2.variables,
                                   phi2.cardinalities,
                                   phi2.values,
                                   phi2.left_hand_side,
                                   phi2.right_hand_side,
                                   phi2.evidence)
    return Potential(phi_variables, phi_cardinalities, phi_values,
                     phi_left_hand_side, phi_right_hand_side, phi_evidence)


def multiply_all(potentials):
    product = None
    first_run = True
    for potential in potentials:
        if first_run:
            product = potential
            first_run = False
        else:
            product = multiply(product, potential)
    return product


def divide(phi1, phi2):
    (phi_variables, phi_cardinalities, phi_values, phi_left_hand_side,
     phi_right_hand_side) = potential_division(phi1.variables,
                                               phi1.cardinalities,
                                               phi1.values,
                                               phi1.left_hand_side,
                                               phi1.right_hand_side,
                                               phi1.evidence,
                                               phi2.variables,
                                               phi2.cardinalities,
                                               phi2.values,
                                               phi2.left_hand_side,
                                               phi2.right_hand_side,
                                               phi2.evidence)
    return Potential(phi_variables, phi_cardinalities, phi_values,
                     phi_left_hand_side, phi_right_hand_side)


def marginalize(phi, sum_variables):
    (potential_variables, potential_cardinalities, potential_values,
     potential_left_hand_side, potential_right_hand_side) = \
        potential_marginalization(phi.variables,
                                  phi.cardinalities,
                                  phi.values,
                                  phi.left_hand_side,
                                  phi.right_hand_side,
                                  sum_variables)
    return Potential(potential_variables, potential_cardinalities,
                     potential_values, potential_left_hand_side,
                     potential_right_hand_side, phi.evidence)


def evidence(set_phi, evidence):
    """
    Incorporate evidence by removing rows that not agree with evidence
    from all potentials containing the evidence variables
    """

    if not isinstance(set_phi, list):
        set_phi = [set_phi]

    normalized = []

    for phi in set_phi:
        evidence_in_phi = {var: v for var, v in evidence.items()
                           if var in phi.variables}
        if len(evidence_in_phi) > 0:
            (potential_variables,
             potential_cardinalities,
             potential_values,
             potential_left_hand_side,
             potential_right_hand_side) \
              = potential_select_evidence(
                phi.variables,
                phi.cardinalities,
                phi.values,
                phi.left_hand_side,
                phi.right_hand_side,
                evidence_in_phi
            )
            normalized.append(
                Potential(potential_variables, potential_cardinalities,
                          potential_values, potential_left_hand_side,
                          potential_right_hand_side, evidence_in_phi
                          )
            )
        else:
            normalized.append(phi)
    return normalized


def normalize(phi):
    potential_values = potential_normalization(phi.values)
    return Potential(phi.variables, phi.cardinalities,
                     potential_values, phi.left_hand_side,
                     phi.right_hand_side, phi.evidence)
