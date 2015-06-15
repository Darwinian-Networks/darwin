from darwin.utils.compute_strides import compute_strides
from darwin.utils.structure_combination import structure_combination
from darwin.utils.structure_operation import structure_operation
from itertools import zip_longest
from functools import reduce
from operator import mul
import numpy as np


def factor_operation(phi1_variables, phi1_cardinalities, phi1_values,
                     phi2_variables, phi2_cardinalities, phi2_values,
                     phi1_left_hand_side, phi1_right_hand_side,
                     phi2_left_hand_side, phi2_right_hand_side,
                     operation):

    # Combine variables and cardinalities of both potentials
    phi_variables, phi_cardinalities = structure_combination(
        phi1_variables, phi1_cardinalities,
        phi2_variables, phi2_cardinalities
    )

    phi1_strides = compute_strides(phi1_variables, phi1_cardinalities,
                                   phi2_variables)
    phi2_strides = compute_strides(phi2_variables, phi2_cardinalities,
                                   phi1_variables)

    # Constants for jumping in j and i
    j_star = {}
    k_star = {}
    for idx, variable in zip_longest(reversed(range(len(phi_variables))),
                                     reversed(phi_variables)):
        j_star[variable] = (
            phi_cardinalities[idx] - 1) * phi1_strides[variable]
        k_star[variable] = (
            phi_cardinalities[idx] - 1) * phi2_strides[variable]
    # Counter for the assignments within the domain cardinalities of variables
    assignment = {var: 0 for var in phi_variables}
    # Loop building the product table
    quantity_values = reduce(mul, phi_cardinalities, 1)
    phi_values = np.zeros(quantity_values)
    j = 0
    k = 0
    # For each row in final potential
    for i in range(quantity_values):
        if operation == "M":
            phi_values[i] = phi1_values[j] * phi2_values[k]
        elif operation == "D":
            # Zero division should return zero
            if phi2_values[k] == 0:
                phi_values[i] = 0
            else:
                phi_values[i] = phi1_values[j] / phi2_values[k]
        # For each column in final potential
        for idx, variable in zip_longest(reversed(range(len(phi_variables))),
                                         reversed(phi_variables)):
            assignment[variable] = assignment[variable] + 1
            if assignment[variable] == phi_cardinalities[idx]:
                assignment[variable] = 0
                j = j - j_star[variable]
                k = k - k_star[variable]
            else:
                j = j + phi1_strides[variable]
                k = k + phi2_strides[variable]
                break

    # Construct the product Factor
    phi_left_hand_side, phi_right_hand_side = structure_operation(
        phi1_left_hand_side, phi1_right_hand_side,
        phi2_left_hand_side, phi2_right_hand_side,
        operation)

    return (phi_variables, phi_cardinalities, phi_values, phi_left_hand_side,
            phi_right_hand_side)
