from darwin.utils.factor_operation import factor_operation
from darwin.utils.factor_marginalization import factor_marginalization
import numpy as np


class Potential:

    def __init__(self, variables, cardinalities, values,
                 left_hand_side=[], right_hand_side=[]):

        self.variables = variables
        self.cardinalities = cardinalities
        self.values = np.array(values)
        self.left_hand_side = left_hand_side
        self.right_hand_side = right_hand_side

    def __str__(self):
        print_out = "p({}|{}) -> {} -> {}".format(
            ",".join(self.left_hand_side),
            ",".join(self.right_hand_side),
            ",".join(self.variables),
            self.values)
        return print_out

    def __hash__(self):
        """
        Returns the hash of the factor object based on the scope of the factor
        """
        return hash(' '.join(self.variables) +
                    ' '.join(map(str, self.cardinalities)) +
                    ' '.join(list(map(str, self.values))))

    def __eq__(self, other):
        """
        Equality between two potential
        """
        return self.__hash__() == other.__hash__()


def multiply(phi1, phi2):
    (phi_variables, phi_cardinalities, phi_values, phi_left_hand_side,
     phi_right_hand_side) = factor_operation(phi1.variables,
                                             phi1.cardinalities,
                                             phi1.values,
                                             phi2.variables,
                                             phi2.cardinalities,
                                             phi2.values,
                                             phi1.left_hand_side,
                                             phi1.right_hand_side,
                                             phi2.left_hand_side,
                                             phi2.right_hand_side,
                                             "M")
    return Potential(phi_variables, phi_cardinalities, phi_values,
                     phi_left_hand_side, phi_right_hand_side)


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


def devide(phi1, phi2):
    (phi_variables, phi_cardinalities, phi_values, phi_left_hand_side,
     phi_right_hand_side) = factor_operation(phi1.variables,
                                             phi1.cardinalities,
                                             phi1.values,
                                             phi2.variables,
                                             phi2.cardinalities,
                                             phi2.values,
                                             phi1.left_hand_side,
                                             phi1.right_hand_side,
                                             phi2.left_hand_side,
                                             phi2.right_hand_side,
                                             "D")
    return Potential(phi_variables, phi_cardinalities, phi_values,
                     phi_left_hand_side, phi_right_hand_side)


def marginalize(phi, sum_variables):
    (potential_variables, potential_cardinalities, potential_values,
     potential_left_hand_side, potential_right_hand_side) = \
        factor_marginalization(phi.variables,
                               phi.cardinalities,
                               phi.values,
                               phi.left_hand_side,
                               phi.right_hand_side,
                               sum_variables)
