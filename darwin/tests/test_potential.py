import unittest
from darwin.potential import *



class TestPotential(unittest.TestCase):

    def setUp(self):
        self.pot_a_ = Potential(["a"], [2],
                                [0.2, 0.8], ["a"], [])
        self.pot_b_a = Potential(["a", "b"], [2, 2],
                                 [0.4, 0.5, 0.6, 0.5], ["b"], ["a"])
        self.pot_c_b = Potential(["b", "c"], [2, 2],
                                 [0.0, 0.2, 1.0, 0.8], ["c"], ["b"])
        self.pot_d_ac = Potential(["a", "c", "d"], [2, 2, 2],
                                  [0.1, 0.8, 0.5, 0.3, 0.9, 0.2, 0.5, 0.7],
                                  ["d"], ["b", "a"])
        self.pot_bc_ = Potential(["b", "c"], [2, 2],
                                 [0.0, 0.104, 0.48, 0.416], ["b", "c"], [])
        self.pot_bcd_ = Potential(["b", "c", "d"], [2, 2, 2],
                                  [0.0, 0.0664, 0.16, 0.144, 0.0, 0.0376, 0.32, 0.272],
                                  ["b", "c", "d"], [])
        self.pot_abcd_ = Potential(["a", "b", "c", "d"], [2, 2, 2, 2],
                                   [0.0, 0.0, 0.0024, 0.064, 0.04, 0.12, 0.048,
                                    0.096, 0.0, 0.0, 0.0216, 0.016, 0.04, 0.28,
                                    0.048, 0.224],
                                   ["a", "b", "c", "d"], [])
        self.pot_a0bcd_ = Potential(["a", "b", "c", "d"], [2, 2, 2, 2],
                                   [0.0, 0.0024, 0.04, 0.048, 0.0, 0.0216, 0.04, 
                                    0.048],
                                   ["a", "b", "c", "d"], [], {"a":0})

    def test_multiply(self):
        pot_ab_ = multiply(self.pot_a_, self.pot_b_a)
        self.assertListEqual([round(elem, 4) for elem in pot_ab_.values],
                             [0.08, 0.40, 0.12, 0.40])

        pot_abc_ = multiply(pot_ab_, self.pot_c_b)
        self.assertListEqual([round(elem, 4) for elem in pot_abc_.values],
                             [0.0, 0.0, 0.024, 0.08, 0.08, 0.40, 0.096, 0.32])

        pot_abcd_ = multiply(pot_abc_, self.pot_d_ac)
        self.assertListEqual([round(elem, 4) for elem in pot_abcd_.values],
                             [0.0, 0.0, 0.0024, 0.064, 0.04, 0.12, 0.048,
                              0.096, 0.0, 0.0, 0.0216, 0.016, 0.04, 0.28,
                              0.048, 0.224])

    def test_multiply_all(self):
        pot_abc_ = multiply_all([self.pot_a_, self.pot_b_a, self.pot_c_b])
        self.assertListEqual([round(elem, 4) for elem in pot_abc_.values],
                             [0.0, 0.0, 0.024, 0.08, 0.08, 0.40, 0.096, 0.32])

        pot_abcd_ = multiply_all([self.pot_a_, self.pot_b_a, self.pot_c_b,
                                  self.pot_d_ac])
        self.assertListEqual([round(elem, 4) for elem in pot_abcd_.values],
                             [0.0, 0.0, 0.0024, 0.064, 0.04, 0.12, 0.048,
                              0.096, 0.0, 0.0, 0.0216, 0.016, 0.04, 0.28,
                              0.048, 0.224])

    def test_divide(self):
        pot_ad_bc = divide(self.pot_abcd_, self.pot_bc_)
        ExpectedValues_pot_ad_bc = [0.0, 0.0, 0.023077, 0.615384, 0.083335, 
                                    0.249999, 0.115385, 0.230769, 0.0, 0.0, 
                                    0.207693, 0.153846, 0.083335, 0.583331,
                                    0.115385, 0.538461]
        self.assertListEqual([round(elem, 4) for elem in pot_ad_bc.values],
                             [round(elem, 4) for elem in ExpectedValues_pot_ad_bc])

        pot_d_bc = divide(self.pot_bcd_, self.pot_bc_)
        ExpectedValues_pot_d_bc = [0.0, 0.638461, 0.33333, 0.346154, 0.0, 
                                   0.36153838, 0.66667, 0.653846]
        self.assertListEqual([round(elem, 4) for elem in pot_d_bc.values],
                             [round(elem, 4) for elem in ExpectedValues_pot_d_bc])

    def test_marginalize(self):
        pot_bc_ = marginalize(self.pot_abcd_, ["a", "d"])
        self.assertListEqual([round(elem, 4) for elem in pot_bc_.values],
                             [round(elem, 4) for elem in self.pot_bc_.values])

        pot_bc_ = marginalize(self.pot_bcd_, ["d"])
        self.assertListEqual([round(elem, 4) for elem in pot_bc_.values],
                             [round(elem, 4) for elem in self.pot_bc_.values])

        pot_b_ = marginalize(pot_bc_, ["c"])
        self.assertListEqual([round(elem, 4) for elem in pot_b_.values],
                             [0.48, 0.52])

    def test_evidence(self):
        list_1 = evidence([self.pot_a_], {"a":0})
        self.assertListEqual([round(elem, 4) for elem in list_1[0].values],
                             [0.2])

        list_2 = evidence([self.pot_a_, self.pot_b_a, self.pot_abcd_], {"a":0})
        self.assertListEqual([round(elem, 4) for elem in list_2[0].values],
                             [0.2])
        self.assertListEqual([round(elem, 4) for elem in list_2[1].values],
                             [0.4, 0.6])       
        self.assertListEqual([round(elem, 4) for elem in list_2[2].values],
                             [0.0, 0.0024, 0.04, 0.048, 0.0, 0.0216, 0.04, 
                              0.048])


        evidence_a0_list_2 = [list_2[0].evidence["a"], list_2[1].evidence["a"], list_2[2].evidence["a"]]
        self.assertListEqual(evidence_a0_list_2, [0, 0, 0])

        list_3 = evidence(list_2, {"b":1})
        self.assertListEqual([round(elem, 4) for elem in list_3[0].values],
                             [0.2])
        self.assertListEqual([round(elem, 4) for elem in list_3[1].values],
                             [0.6])       
        self.assertListEqual([round(elem, 4) for elem in list_3[2].values],
                             [0.0024, 0.048, 0.0216, 0.048])

        # list_4 = evidence([self.pot_a_, self.pot_b_a, self.pot_abcd_], {"a":0, "b":1})

    def test_normalize(self):
        npot_a0bcd_ = normalize(self.pot_a0bcd_)
        self.assertListEqual([round(elem, 4) for elem in npot_a0bcd_.values],
                             [0.0, 0.012, 0.2, 0.24, 0.0, 0.108, 0.2, 
                              0.24])
