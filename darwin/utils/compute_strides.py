

def compute_strides(phi1_variables, phi1_cardinalities,
                    phi2_variables=None):
    """
    Compute strides for table phi1.
    Stride of a variable is equal to the stride of the previous variable
    times the cardinality of the previous variable
    If phi2 is given, add strides zero for variables in phi2 but not in phi1
    """
    phi1_strides = {}
    first_run = True
    for i in reversed(range(len(phi1_variables))):
        if first_run:
            phi1_strides[phi1_variables[i]] = 1
            first_run = False
            pass
        else:
            phi1_strides[phi1_variables[i]] = phi1_strides[
                phi1_variables[i + 1]] * phi1_cardinalities[i + 1]
    if phi2_variables:
        for var in phi2_variables:
            if var not in phi1_strides:
                phi1_strides[var] = 0
    return phi1_strides
