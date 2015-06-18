from darwin.potential import multiply_all, marginalize


def sum_out(variables, potentials):

    if not isinstance(variables, (list, set)):
        variables = [variables]

    set_potentials = [p for p in potentials]
    for var in variables:
        # Get all potentials involving var
        common_potentials = [p for p in set_potentials
                             if var in p.variables]
        product = multiply_all(common_potentials)
        marg_product = marginalize(product, var)
        # Update the set of potentials
        set_potentials = [p for p in set_potentials
                          if p not in common_potentials]

        set_potentials.append(marg_product)

    return set_potentials
