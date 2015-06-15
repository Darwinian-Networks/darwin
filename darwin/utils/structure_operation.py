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
