from functools import reduce
from operator import mul


def potential_multiplication(phi1_variables, phi1_cardinalities, phi1_values,
                             phi1_left_hand_side, phi1_right_hand_side,
                             phi1_evidence,
                             phi2_variables, phi2_cardinalities, phi2_values,
                             phi2_left_hand_side, phi2_right_hand_side,
                             phi2_evidence):
    return potential_operation(phi1_variables, phi1_cardinalities, phi1_values,
                               phi1_left_hand_side, phi1_right_hand_side,
                               phi1_evidence,
                               phi2_variables, phi2_cardinalities, phi2_values,
                               phi2_left_hand_side, phi2_right_hand_side,
                               phi2_evidence, 'M')


def potential_division(phi1_variables, phi1_cardinalities, phi1_values,
                       phi1_left_hand_side, phi1_right_hand_side,
                       phi1_evidence,
                       phi2_variables, phi2_cardinalities, phi2_values,
                       phi2_left_hand_side, phi2_right_hand_side,
                       phi2_evidence):
    return potential_operation(phi1_variables, phi1_cardinalities, phi1_values,
                               phi1_left_hand_side, phi1_right_hand_side,
                               phi1_evidence,
                               phi2_variables, phi2_cardinalities, phi2_values,
                               phi2_left_hand_side, phi2_right_hand_side,
                               phi2_evidence, 'D')


def potential_operation(phi1_variables, phi1_cardinalities, phi1_values,
                        phi1_left_hand_side, phi1_right_hand_side,
                        phi1_evidence,
                        phi2_variables, phi2_cardinalities, phi2_values,
                        phi2_left_hand_side, phi2_right_hand_side,
                        phi2_evidence, operation):

    # Combine variables and cardinalities of both potentials
    potential_variables, potential_cardinalities \
        = structure_combination(
            phi1_variables, phi1_cardinalities,
            phi2_variables, phi2_cardinalities
        )
    potential_evidence = evidence_combination(phi1_evidence, phi2_evidence)

    phi1_strides = compute_strides(phi1_variables, phi1_cardinalities,
                                   phi2_variables)
    phi2_strides = compute_strides(phi2_variables, phi2_cardinalities,
                                   phi1_variables)

    assignment = {var: 0 for var in potential_variables}
    potential_size = reduce(mul, potential_cardinalities, 1)
    potential_values = [0] * potential_size

    j = 0
    k = 0
    for i in range(potential_size):
        if operation == "M":
            potential_values[i] = phi1_values[j] * phi2_values[k]
        elif operation == "D":
            if phi2_values[k] == 0:  # Division by zero returns zero
                potential_values[i] = 0
            else:
                potential_values[i] = phi1_values[j] / phi2_values[k]

        for idx, var in enumerate(potential_variables):
            assignment[var] = assignment[var] + 1
            if assignment[var] == potential_cardinalities[idx]:
                assignment[var] = 0
                j = j - (potential_cardinalities[idx] - 1) * phi1_strides[var]
                k = k - (potential_cardinalities[idx] - 1) * phi2_strides[var]
            else:
                j = j + phi1_strides[var]
                k = k + phi2_strides[var]
                break

    # Construct the product Factor
    potential_left_hand_side, potential_right_hand_side = structure_operation(
        phi1_left_hand_side, phi1_right_hand_side,
        phi2_left_hand_side, phi2_right_hand_side,
        operation)

    return (potential_variables, potential_cardinalities,
            potential_values, potential_left_hand_side,
            potential_right_hand_side, potential_evidence)


def potential_marginalization(phi_variables, phi_cardinalities, phi_values,
                              phi_left_hand_side, phi_right_hand_side,
                              sum_variables):

    if not isinstance(sum_variables, list):
        sum_variables = [sum_variables]

    # Compute variables and caridnalities for new potential
    potential_variables, potential_cardinalities = structure_reducing(
        phi_variables, phi_cardinalities, sum_variables)

    # Compute LHS and RHS for new potential
    potential_left_hand_side, potential_right_hand_side = \
        structure_merginalization(
            phi_left_hand_side, phi_right_hand_side, sum_variables)

    # Compute strides
    phi_strides = compute_strides(phi_variables,
                                  phi_cardinalities,
                                  potential_variables)
    potential_strides = compute_strides(potential_variables,
                                        potential_cardinalities,
                                        phi_variables)

    # Start computation of values for marginalized potential
    potential_values = None
    if len(potential_variables) > 0:

        assignment = {var: 0 for var in phi_variables}
        potential_size = reduce(mul, potential_cardinalities, 1)
        potential_values = [0] * potential_size
        phi_size = reduce(mul, phi_cardinalities, 1)

        j = 0
        k = 0
        while True:

            potential_values[k] += phi_values[j]

            if j == (phi_size - 1):
                break

            for idx, var in enumerate(phi_variables):
                assignment[var] += 1
                if assignment[var] == phi_cardinalities[idx]:
                    assignment[var] = 0
                    j -= (phi_cardinalities[idx] - 1) * phi_strides[var]
                    k -= (phi_cardinalities[idx] - 1
                          ) * potential_strides[var]
                else:
                    j += phi_strides[var]
                    k += potential_strides[var]
                    break
    else:
        potential_values = [sum(phi_values)]

    return (potential_variables, potential_cardinalities,
            potential_values,
            potential_left_hand_side, potential_right_hand_side)


def potential_select_evidence(phi_variables, phi_cardinalities, phi_values,
                              phi_left_hand_side, phi_right_hand_side,
                              evidence):

    evidence_variables = list(evidence.keys())

    # Compute variables and caridnalities for new potential
    potential_variables, potential_cardinalities = structure_reducing(
        phi_variables, phi_cardinalities, evidence_variables)

    # Compute LHS and RHS for new potential
    potential_left_hand_side, potential_right_hand_side = \
        structure_merginalization(
            phi_left_hand_side, phi_right_hand_side, evidence_variables)

    # Start computation of values for marginalized potential
    potential_values = None

    assignment = {var: 0 for var in phi_variables}
    potential_size = reduce(mul, potential_cardinalities, 1)
    phi_size = reduce(mul, phi_cardinalities, 1)
    if potential_size > 0:
        potential_values = [0] * potential_size
    else:
        potential_values = [0]

    j = 0
    for i in range(phi_size):
        if all([assignment[evidence_var] == evidence[evidence_var]
                for evidence_var in evidence]):
            potential_values[j] = phi_values[i]
            j = j + 1

        for idx, var in enumerate(phi_variables):
            assignment[var] += 1
            if assignment[var] == phi_cardinalities[idx]:
                assignment[var] = 0
            else:
                break

    return (potential_variables, potential_cardinalities,
            potential_values,
            potential_left_hand_side, potential_right_hand_side)


def potential_normalization(phi_values):
    total_sum = sum(phi_values)
    return [value / total_sum for value in phi_values]


def compute_strides(phi1_variables, phi1_cardinalities,
                    phi2_variables=None):
    """
    Compute strides for table phi1.
    Stride of a variable is equal to the stride of the previous variable
    times the cardinality of the previous variable
    If phi2 is given, add strides zero for variables in phi2 but not in phi1
    """
    phi1_strides = {var: 0 for var in phi1_variables}
    first_run = True
    for i in range(len(phi1_variables)):
        if first_run:
            phi1_strides[phi1_variables[i]] = 1
            first_run = False
            pass
        else:
            phi1_strides[phi1_variables[i]] = \
                phi1_strides[phi1_variables[i - 1]] * phi1_cardinalities[i - 1]
    if phi2_variables:
        for var in phi2_variables:
            if var not in phi1_variables:
                phi1_strides[var] = 0
    return phi1_strides


def structure_combination(phi1_variables, phi1_cardinalities,
                          phi2_variables, phi2_cardinalities):
    """
    Combine variables and cardinalities (used in multiplication and division)
    """
    variables = list(phi1_variables)
    cardinalities = list(phi1_cardinalities)

    for (ind, var) in enumerate(phi2_variables):
        if var not in phi1_variables:
            variables.append(var)
            cardinalities.append(phi2_cardinalities[ind])

    return (variables, cardinalities)


def evidence_combination(phi1_evidence, phi2_evidence):
    evidence = dict(phi1_evidence)
    for var in phi2_evidence:
        if var not in evidence:
            evidence[var] = phi2_evidence[var]
    return evidence


def structure_operation(phi1_left_hand_side, phi1_right_hand_side,
                        phi2_left_hand_side, phi2_right_hand_side,
                        operation):
    """
    Combine left hand side and right hand side depending on the
    operation performed (used in multiplication and division)
    """
    left_hand_side = list(phi1_left_hand_side)
    left_hand_side.extend([var for var in phi2_left_hand_side
                           if var not in phi1_left_hand_side])
    right_hand_side = []
    if operation == 'D':
        left_hand_side = [v for v in left_hand_side
                          if v not in phi2_left_hand_side]
        right_hand_side = [var for var in phi2_left_hand_side]
    right_hand_side.extend([var for var in phi1_right_hand_side
                            if (var not in left_hand_side)])
    right_hand_side.extend([var for var in phi2_right_hand_side
                            if (var not in left_hand_side) and (
                                var not in right_hand_side)])
    return (left_hand_side, right_hand_side)


def structure_merginalization(phi_left_hand_side, phi_right_hand_side,
                              sum_variables):
    """
    reduce left hand side and right hand for marginalized variables
    (used in marginalization)
    """
    left_hand_side = [v for v in phi_left_hand_side
                      if v not in sum_variables]
    right_hand_side = [v for v in phi_right_hand_side
                       if v not in sum_variables]
    return (left_hand_side, right_hand_side)


def structure_reducing(phi_variables, phi_cardinalities, sum_variables):
    """
    Reduce variables and cardinalities  (marginalization)
    """
    variables = []
    cardinalities = []
    for i, var in enumerate(phi_variables):
        if var not in sum_variables:
            variables.append(var)
            cardinalities.append(phi_cardinalities[i])

    return (variables, cardinalities)
