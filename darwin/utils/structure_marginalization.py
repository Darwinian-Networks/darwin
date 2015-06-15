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
