from itertools import zip_longest
from functools import reduce
from operator import mul
import numpy as np
from darwin.utils.compute_strides import compute_strides
from darwin.utils.structure_reducing import structure_reducing
from darwin.utils.structure_marginalization import structure_merginalization


def factor_marginalization(phi_variables, phi_cardinalities, phi_values,
                           phi_left_hand_side, phi_right_hand_side,
                           sum_variables):

    if not isinstance(sum_variables, list):
        sum_variables = [sum_variables]

    potential_variables, potential_cardinalities = structure_reducing(
        phi_variables, phi_cardinalities, sum_variables)

    potential_left_hand_side, potential_right_hand_side = \
        structure_merginalization(
            phi_left_hand_side, phi_right_hand_side, sum_variables)

    quantity_values = reduce(mul, potential_cardinalities, 1)
    potential_values = np.zeros(quantity_values)

    # Compute strides
    strides = compute_strides(potential_variables,
                              potential_cardinalities,
                              phi_variables)

    # common used lists
    reversed_range_vars = list(reversed(range(len(phi_variables))))
    reversed_vars = list(reversed(phi_variables))

    # Start computation of values for marginalized potential
    if len(potential_variables) > 0:
        # Constants for jumping in j and i
        j_star = {}
        for idx, variable in zip_longest(reversed_range_vars,
                                         reversed_vars):
            j_star[variable] = (
                phi_cardinalities[idx] - 1) * strides[variable]
        # Counter for the assignments within the
        # domain cardinality of variables
        assignment = {var: 0 for var in phi_variables}
        # Loop building the product table
        j = 0
        for i in range(reduce(mul, phi_cardinalities, 1)):
            potential_values[j] += phi_values[i]
            for idx, variable in zip_longest(reversed_range_vars,
                                             reversed_vars):
                assignment[variable] = assignment[variable] + 1
                if assignment[variable] == phi_cardinalities[idx]:
                    assignment[variable] = 0
                    j = j - j_star[variable]
                else:
                    j = j + strides[variable]
                    break
    else:
        potential_values = np.array([np.sum(phi_values)])

    return (potential_variables, potential_cardinalities,
            potential_values,
            potential_left_hand_side, potential_right_hand_side)
