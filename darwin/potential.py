import numpy as np
from operator import mul
from functools import reduce
from itertools import zip_longest


class Potential:

    def __init__(self, variables, cardinalities, values,
                 left_hand_side=[], right_hand_side=[]):

        self.variables = variables
        self.cardinalities = cardinalities
        self.values = np.array(values)
        self.left_hand_side = left_hand_side
        self.right_hand_side = right_hand_side

    def __str__(self):
        print_out = "p({}|{}) -> {}".format(",".join(self.left_hand_side),
                                            ",".join(self.right_hand_side),
                                            self.values)
        return print_out


def _factor_operation(phi1, phi2, operation):

    # Combine variables and cardinalities of both potentials
    variables, cardinalities = _structure_combination(phi1, phi2)

    phi1_strides = _compute_strides(phi1, phi2)
    phi2_strides = _compute_strides(phi2, phi1)

    # Constants for jumping in j and i
    j_star = {}
    k_star = {}
    for idx, variable in zip_longest(reversed(range(len(variables))),
                                     reversed(variables)):
        j_star[variable] = (cardinalities[idx] - 1) * phi1_strides[variable]
        k_star[variable] = (cardinalities[idx] - 1) * phi2_strides[variable]
    # Counter for the assignments within the domain cardinalities of variables
    assignment = {var: 0 for var in variables}
    # Loop building the product table
    quantity_values = reduce(mul, cardinalities, 1)
    values = np.zeros(quantity_values)
    j = 0
    k = 0
    # For each row in final potential
    for i in range(quantity_values):
        if operation == "M":
            values[i] = phi1.values[j] * phi2.values[k]
        elif operation == "D":
            # Zero division should return zero
            if phi2.values[k] == 0:
                values[i] = 0
            else:
                values[i] = phi1.values[j] / phi2.values[k]
        # For each column in final potential
        for idx, variable in zip_longest(reversed(range(len(variables))),
                                         reversed(variables)):
            assignment[variable] = assignment[variable] + 1
            if assignment[variable] == cardinalities[idx]:
                assignment[variable] = 0
                j = j - j_star[variable]
                k = k - k_star[variable]
            else:
                j = j + phi1_strides[variable]
                k = k + phi2_strides[variable]
                break

    # Construct the product Factor
    phi = Potential(variables, cardinalities, values)
    phi.left_hand_side, phi.right_hand_side = _structure_operation(
        phi1, phi2, operation)

    return phi


def _factor_marginalization(phi, sum_variables):

    if not isinstance(sum_variables, list):
        sum_variables = [sum_variables]

    variables, cardinalities = _structure_reducing(phi, sum_variables)
    left_hand_side, right_hand_side = _structure_merginalization(
        phi, sum_variables)

    potential = Potential(variables, cardinalities, [],
                          left_hand_side, right_hand_side)
    quantity_values = reduce(mul, cardinalities, 1)
    potential.values = np.zeros(quantity_values)

    # # Remove marginalized variables.
    # old_factor_vars = potential.scope()
    # card_ind = []
    # for (ind, var) in enumerate(potential.variables):
    #     if var in variables:
    #         del(potential.variables[var])
    #     else:
    #         card_ind.append(ind)

    # new_factor_cardinality = potential.cardinalities[card_ind]

    # quantity_values = np.prod(new_factor_cardinality)
    # values = np.zeros(quantity_values)
    # strides = {var: stride
    #                       for (var, stride) in zip(
    #                           potential.scope(),
    #                           np.delete(
    #                               np.concatenate(
    #                                   (np.array([1]),
    #                                    np.cumprod(
    #                                       new_factor_cardinality[::-1])
    #                                    ),
    #                                   axis=1)[::-1], 0))}
    # for var in variables:
    #     strides[var] = 0

    # common used lists
    reversed_range_vars = list(reversed(range(len(phi.variables))))
    reversed_vars = list(reversed(phi.variables))

    # Compute strides
    strides = _compute_strides(potential, phi)

    # Start computation of values for marginalized potential
    if len(potential.variables) > 0:
        # Constants for jumping in j and i
        j_star = {}
        for idx, variable in zip_longest(reversed_range_vars,
                                         reversed_vars):
            j_star[variable] = (
                phi.cardinalities[idx] - 1) * strides[variable]
        # Counter for the assignments within the
        # domain cardinality of variables
        assignment = {var: 0 for var in phi.variables}
        # Loop building the product table
        j = 0
        for i in range(reduce(mul, phi.cardinalities, 1)):
            potential.values[j] += phi.values[i]
            for idx, variable in zip_longest(reversed_range_vars,
                                             reversed_vars):
                assignment[variable] = assignment[variable] + 1
                if assignment[variable] == phi.cardinalities[idx]:
                    assignment[variable] = 0
                    j = j - j_star[variable]
                else:
                    j = j + strides[variable]
                    break
    else:
        potential.values = np.array([np.sum(phi.values)])

    # # Record the cardinality
    # potential.cardinalities = new_factor_cardinality

    # # Fixing the LHS and RHS by removing marginalized variables
    # potential.left_hand_side = list(set(potential.left_hand_side)
    #                              - set(variables))
    # potential.right_hand_side = list(set(potential.right_hand_side)
    #                               - set(variables))

    return potential


def _structure_reducing(phi, sum_variables):
    """
    Reduce variables and cardinalities  (marginalization)
    """
    variables = []
    cardinalities = []
    for i, var in enumerate(phi.variables):
        if var not in sum_variables:
            variables.append(var)
            cardinalities.append(phi.cardinalities[i])

    return (variables, cardinalities)


def _structure_combination(phi1, phi2):
    """
    Combine variables and cardinalities (used in multiplication and division)
    """
    variables = list(phi1.variables)
    cardinalities = list(phi1.cardinalities)

    for (ind, var) in enumerate(phi2.variables):
        if var not in phi1.variables:
            variables.append(var)
            cardinalities.append(phi2.cardinalities[ind])
    return (variables, cardinalities)


def _structure_merginalization(phi, sum_variables):
    """
    reduce left hand side and right hand for marginalized variables
    (used in marginalization)
    """
    left_hand_side = [v for v in phi.left_hand_side
                      if v not in sum_variables]
    right_hand_side = [v for v in phi.right_hand_side
                       if v not in sum_variables]
    return (left_hand_side, right_hand_side)


def _structure_operation(phi1, phi2, operation):
    """
    Combine left hand side and right hand side depending on the
    operation performed (used in multiplication and division)
    """
    left_hand_side = list(phi1.left_hand_side)
    left_hand_side.extend([var for var in phi2.left_hand_side
                           if var not in phi1.left_hand_side])
    right_hand_side = []
    if operation == 'D':
        left_hand_side = [v for v in left_hand_side
                          if v not in phi2.left_hand_side]
        right_hand_side = [var for var in phi2.left_hand_side]
    right_hand_side.extend([var for var in phi1.right_hand_side
                            if (var not in left_hand_side)])
    right_hand_side.extend([var for var in phi2.right_hand_side
                            if (var not in left_hand_side)])
    return (left_hand_side, right_hand_side)


# Compute strides for table phi1.
# Stride of a variable is equal to the stride of the previous variable
# times the cardinality of the previous variable
# If phi2 is given, add strides zero for variables in phi2 but not in phi1
def _compute_strides(phi1, phi2=None):
    phi1_strides = {}
    first_run = True
    for i in reversed(range(len(phi1.variables))):
        if first_run:
            phi1_strides[phi1.variables[i]] = 1
            first_run = False
            pass
        else:
            phi1_strides[phi1.variables[i]] = phi1_strides[
                phi1.variables[i - 1]] * phi1.cardinalities[i - 1]
    if phi2:
        for var in phi2.variables:
            if var not in phi1_strides:
                phi1_strides[var] = 0
    return phi1_strides
