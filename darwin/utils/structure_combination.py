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
