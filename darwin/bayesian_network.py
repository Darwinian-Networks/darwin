class BayesianNetwork:

    def __init__(self):
        self.potentials = []
        self.dag = None

    def add_potential(self, potential):
        self.potentials.append(potential)

    def add_dag(self, dag):
        self.dag = dag

    def get_cpt(self, variable):
        possible_cpts = [p for p in self.potentials
                         if variable in p.left_hand_side]
        return possible_cpts[0]
