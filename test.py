from darwin.potential import Potential, _factor_operation, _factor_marginalization


print()
print(">>> Multiplying and Dividing")

phi1 = Potential(['a', 'b'], [2, 3],
                 [0.2, 0.4, 0.4, 0.7, 0.2, 0.1], ['a'], ['b'])
print(phi1)

phi2 = Potential(['b'], [3], [0.4, 0.1, 0.5], ['b'])
print(phi2)

phi3 = _factor_operation(phi1, phi2, 'M')
print(phi3)

phi4 = _factor_operation(phi3, phi2, 'D')
print(phi4)

print()
print(">>> Marginalizing")
phi5 = _factor_marginalization(phi3, 'b')
print(phi5)
