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
