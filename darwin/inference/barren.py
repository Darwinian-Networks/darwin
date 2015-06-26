def remove_barren(vars_to_sum_out, potentials):

    non_barren_potentials = [p for p in potentials]
    while True:
        changed = False
        for var in vars_to_sum_out:
            potentials_involving_var = [p for p in non_barren_potentials
                                        if var in p.variables]
            if len(potentials_involving_var) == 1 and len(
                    potentials_involving_var[0].left_hand_side) == 1:
                non_barren_potentials.remove(potentials_involving_var[0])
                changed = True
                break
        if not changed:
            break
    return non_barren_potentials
