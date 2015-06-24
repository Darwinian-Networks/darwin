from darwin.inference.barren import remove_barren
from darwin.potential import multiply_all, marginalize


def sum_out(variables, potentials, is_to_remove_barren=False):

    if not isinstance(variables, (list, set)):
        variables = [variables]

    set_potentials = [p for p in potentials]
    # If remove barren (extra computation)
    if is_to_remove_barren:
        set_potentials = remove_barren(variables, set_potentials)
    for var in variables:
        # Get all potentials involving var
        common_potentials = [p for p in set_potentials
                             if var in p.variables]
        # If has potentials involving var
        if len(common_potentials) > 0:
            # Perform sum out
            product = multiply_all(common_potentials)
            marg_product = marginalize(product, var)
            # Update the set of potentials
            set_potentials = [p for p in set_potentials
                              if p not in common_potentials]

            set_potentials.append(marg_product)

    return set_potentials
